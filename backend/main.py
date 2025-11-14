from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import pandas as pd
import os
import numpy as np
import json

from contextlib import asynccontextmanager

from services.news_scraper import NewsScraper
from services.sentiment_analyzer import SentimentAnalyzer
from services.signal_calculator import SignalCalculator
from commodity_config import COMMODITIES, get_commodity_config, get_available_commodities

# Initialize services
sentiment_analyzer = SentimentAnalyzer()
signal_calculator = SignalCalculator()

# Cache for loaded commodity data
commodity_data_cache = {}

def load_commodity_data(commodity: str):
    """Load data for a specific commodity"""
    import logging
    logger = logging.getLogger(__name__)
    global commodity_data_cache
    
    if commodity not in commodity_data_cache:
        try:
            logger.info(f"Loading data for commodity: {commodity}")
            config = get_commodity_config(commodity)
            data_path = os.path.join(os.path.dirname(__file__), "..", "data", config['data_file'])
            logger.info(f"Data file path: {data_path}")
            
            if not os.path.exists(data_path):
                raise FileNotFoundError(f"Data file not found: {data_path}")
            
            df = pd.read_csv(data_path)
            logger.info(f"Loaded {len(df)} rows from {config['data_file']}")
            
            # Convert time column to datetime - try multiple formats
            # First try without format to handle ISO dates (YYYY-MM-DD) and other formats
            df['time'] = pd.to_datetime(df['time'], errors='coerce')
            # If some dates failed to parse, try M/D/YY format (for gold.csv) on the failed ones
            if df['time'].isna().any():
                # Only try the second format on rows that failed to parse
                mask = df['time'].isna()
                df.loc[mask, 'time'] = pd.to_datetime(df.loc[mask, 'time'], format='%m/%d/%y', errors='coerce')
            # Remove rows with invalid dates
            df = df.dropna(subset=['time'])
            logger.info(f"After date parsing: {len(df)} rows")
            
            # Filter to start from Sept 1, 2022
            start_date = pd.to_datetime('2022-09-01')
            df = df[df['time'] >= start_date]
            logger.info(f"After filtering from 2022-09-01: {len(df)} rows")
            
            # Sort by date
            df = df.sort_values('time').reset_index(drop=True)
            
            # Log for debugging
            if len(df) == 0:
                logger.warning(f"No data found for {commodity} after filtering from 2022-09-01")
            else:
                logger.info(f"Successfully loaded {len(df)} rows for {commodity}")
            
            commodity_data_cache[commodity] = df
        except Exception as e:
            logger.error(f"Error loading {commodity} data: {str(e)}", exc_info=True)
            raise
    
    return commodity_data_cache[commodity]

def clean_data_for_json(df):
    """Clean DataFrame to make it JSON serializable"""
    # Convert to dict first, then clean NaN values
    records = df.to_dict(orient='records')
    
    # Clean each record
    cleaned_records = []
    for record in records:
        cleaned_record = {}
        for key, value in record.items():
            # Convert datetime to ISO format string
            if isinstance(value, pd.Timestamp):
                cleaned_record[key] = value.isoformat()
            # Convert NaN/NaT to None
            elif pd.isna(value) or (isinstance(value, float) and np.isnan(value)):
                cleaned_record[key] = None
            else:
                cleaned_record[key] = value
        cleaned_records.append(cleaned_record)
    
    return cleaned_records

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - preload all commodity data
    import logging
    logger = logging.getLogger(__name__)
    for commodity in get_available_commodities():
        try:
            load_commodity_data(commodity)
            logger.info(f"✅ Successfully loaded {commodity} data")
        except Exception as e:
            logger.error(f"❌ Failed to load {commodity} data during startup: {str(e)}")
            # Continue loading other commodities even if one fails
    yield
    # Shutdown (if needed)

app = FastAPI(title="Commodity Trading Signal API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Commodity Trading Signal API", "available_commodities": get_available_commodities()}

@app.get("/api/commodities")
async def get_available_commodities_list():
    """Get list of available commodities"""
    commodities = []
    for key in get_available_commodities():
        config = get_commodity_config(key)
        commodities.append({
            "key": key,
            "name": config['name']
        })
    return commodities

@app.get("/api/{commodity}/data")
async def get_commodity_data(commodity: str):
    """Get all price and index data for a commodity"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Received request for commodity: {commodity}")
    
    try:
        # First check if commodity is valid
        try:
            config = get_commodity_config(commodity)
            logger.info(f"Commodity {commodity} is valid, config: {config['name']}")
        except ValueError as e:
            logger.error(f"Invalid commodity: {commodity} - {str(e)}")
            raise HTTPException(status_code=404, detail=f"Unknown commodity: {commodity}. Available: {', '.join(get_available_commodities())}")
        
        # Load the data
        df = load_commodity_data(commodity)
        if df is None or len(df) == 0:
            logger.warning(f"No data available for {commodity} after filtering")
            raise HTTPException(status_code=404, detail=f"No data available for {commodity} after filtering from 2022-09-01")
        
        cleaned_records = clean_data_for_json(df)
        logger.info(f"Returning {len(cleaned_records)} records for {commodity}")
        return cleaned_records
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading {commodity} data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

@app.get("/api/{commodity}/data/date/{target_date}")
async def get_commodity_data_by_date(commodity: str, target_date: str):
    """Get commodity data for a specific date"""
    try:
        df = load_commodity_data(commodity)
        target = pd.to_datetime(target_date)
        # Find closest date
        df['date_diff'] = abs(df['time'] - target)
        closest_row = df.loc[df['date_diff'].idxmin()].drop('date_diff')
        # Clean the row for JSON serialization
        result = {}
        for key, value in closest_row.items():
            if pd.isna(value) or (isinstance(value, float) and np.isnan(value)):
                result[key] = None
            elif isinstance(value, pd.Timestamp):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

@app.get("/api/{commodity}/signal/{target_date}")
async def get_trading_signal(commodity: str, target_date: str):
    """Get trading signal (buy/sell) for a specific date and commodity"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        config = get_commodity_config(commodity)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    logger.info(f"📅 Received signal request for {commodity} on date: {target_date}")
    df = load_commodity_data(commodity)
    
    try:
        target = pd.to_datetime(target_date)
        logger.info(f"📅 Parsed target date: {target}")
        
        # Get price data for target date and previous day
        df['date_diff'] = abs(df['time'] - target)
        closest_idx = df['date_diff'].idxmin()
        current_data = df.loc[closest_idx]
        closest_date = current_data['time']
        
        logger.info(f"📊 Closest price data date: {closest_date} (requested: {target})")
        
        # Get previous day data
        prev_data = df[df['time'] < closest_date].iloc[-1] if len(df[df['time'] < closest_date]) > 0 else None
        
        if prev_data is None:
            raise HTTPException(status_code=404, detail="No previous data available")
        
        # Calculate price change
        current_close = current_data['close']
        prev_close = prev_data['close']
        
        # Handle NaN values
        if pd.isna(current_close) or pd.isna(prev_close):
            raise HTTPException(status_code=404, detail="Price data not available for this date")
        
        price_change = float(current_close) - float(prev_close)
        price_direction = "up" if price_change > 0 else "down" if price_change < 0 else "neutral"
        
        # Scrape news for the USER-SELECTED date (target), not the closest price data date
        logger.info(f"📰 Scraping news for user-selected date: {target}")
        try:
            news_scraper = config['news_scraper']
            news_articles = await news_scraper.scrape_news_for_date(target)
            logger.info(f"📰 Found {len(news_articles)} news articles")
        except Exception as e:
            logger.error(f"❌ Error scraping news: {str(e)}")
            news_articles = []
        
        # Analyze sentiment
        try:
            sentiment_result = await sentiment_analyzer.analyze_sentiment(news_articles)
            news_sentiment = sentiment_result['sentiment']  # 'bullish' or 'bearish'
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            # Fallback to neutral if sentiment analysis fails
            sentiment_result = {'sentiment': 'neutral', 'score': 0.0}
            news_sentiment = 'neutral'
        
        # Calculate signal
        signal = signal_calculator.calculate_signal(price_direction, news_sentiment)
        
        return {
            "date": closest_date.strftime("%Y-%m-%d") if isinstance(closest_date, pd.Timestamp) else str(closest_date),
            "price": float(current_close) if not pd.isna(current_close) else None,
            "previous_price": float(prev_close) if not pd.isna(prev_close) else None,
            "price_change": float(price_change),
            "price_direction": price_direction,
            "news_sentiment": news_sentiment,
            "signal": signal['action'],  # 'buy' or 'sell'
            "reason": signal['reason'],
            "news_count": len(news_articles),
            "sentiment_score": float(sentiment_result.get('score', 0)) if sentiment_result.get('score') is not None else 0.0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating signal: {str(e)}")

@app.get("/api/{commodity}/news/{target_date}")
async def get_news_for_date(commodity: str, target_date: str):
    """Get news articles for a specific date and commodity"""
    try:
        config = get_commodity_config(commodity)
        target = pd.to_datetime(target_date)
        news_scraper = config['news_scraper']
        articles = await news_scraper.scrape_news_for_date(target)
        return {
            "date": target_date,
            "articles": articles
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

