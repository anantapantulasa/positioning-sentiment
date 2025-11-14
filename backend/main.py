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

# Initialize services
news_scraper = NewsScraper()
sentiment_analyzer = SentimentAnalyzer()
signal_calculator = SignalCalculator()

# Load gold data
GOLD_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "gold.csv")
gold_df = None

def load_gold_data():
    global gold_df
    if gold_df is None:
        gold_df = pd.read_csv(GOLD_DATA_PATH)
        # Convert time column to datetime - try multiple formats
        gold_df['time'] = pd.to_datetime(gold_df['time'], format='%m/%d/%y', errors='coerce')
        # If parsing failed, try without format specification
        if gold_df['time'].isna().any():
            gold_df['time'] = pd.to_datetime(gold_df['time'], errors='coerce')
        # Remove rows with invalid dates
        gold_df = gold_df.dropna(subset=['time'])
        # Filter to start from Sept 1, 2022
        start_date = pd.to_datetime('2022-09-01')
        gold_df = gold_df[gold_df['time'] >= start_date]
        # Sort by date
        gold_df = gold_df.sort_values('time').reset_index(drop=True)
    return gold_df

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
    # Startup
    load_gold_data()
    yield
    # Shutdown (if needed)

app = FastAPI(title="Gold Trading Signal API", lifespan=lifespan)

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
    return {"message": "Gold Trading Signal API"}

@app.get("/api/gold/data")
async def get_gold_data():
    """Get all gold price and index data"""
    df = load_gold_data()
    cleaned_records = clean_data_for_json(df)
    return cleaned_records

@app.get("/api/gold/data/date/{target_date}")
async def get_gold_data_by_date(target_date: str):
    """Get gold data for a specific date"""
    df = load_gold_data()
    try:
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
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

@app.get("/api/gold/signal/{target_date}")
async def get_trading_signal(target_date: str):
    """Get trading signal (buy/sell) for a specific date"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"📅 Received signal request for date: {target_date}")
    df = load_gold_data()
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
        # This ensures we get news for the date the user actually selected
        logger.info(f"📰 Scraping news for user-selected date: {target}")
        try:
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

@app.get("/api/gold/news/{target_date}")
async def get_news_for_date(target_date: str):
    """Get news articles for a specific date"""
    try:
        target = pd.to_datetime(target_date)
        articles = await news_scraper.scrape_news_for_date(target)
        return {
            "date": target_date,
            "articles": articles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

