# Gold Trading Signal Dashboard

A full-stack application that analyzes gold commodity prices with sentiment-based trading signals. The system scrapes news from investing.com, analyzes sentiment using Groq API, and generates buy/sell signals based on price movements and news sentiment.

## Features

- **Price Visualization**: Interactive chart showing gold prices over time
- **Index Overlays**: Toggleable overlays for Commercials, Large Speculators, and Small Speculators indices
- **Date Slider**: Navigate through historical data with a date slider
- **Trading Signals**: Real-time buy/sell signals based on:
  - Price direction (up/down)
  - News sentiment (bullish/bearish)
  - Reversal detection when price and sentiment disagree
- **News Scraping**: Automated scraping of gold news from investing.com
- **Sentiment Analysis**: AI-powered sentiment analysis using Groq API

## Project Structure

```
.
├── backend/           # FastAPI backend
│   ├── main.py       # API endpoints
│   ├── services/     # Business logic
│   │   ├── news_scraper.py
│   │   ├── sentiment_analyzer.py
│   │   └── signal_calculator.py
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
└── data/             # Commodity data files
    └── gold.csv
```

## Setup Instructions

### Prerequisites

- Python 3.8+ installed
- Node.js 16+ and npm installed
- Groq API key (get one at https://console.groq.com/)

### Quick Start

1. **Set your Groq API key:**
```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

2. **Start the backend** (in one terminal):
```bash
./start_backend.sh
# Or manually:
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

3. **Start the frontend** (in another terminal):
```bash
./start_frontend.sh
# Or manually:
cd frontend
npm install
npm run dev
```

4. **Open your browser** to `http://localhost:3000`

### Manual Setup

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set your Groq API key as an environment variable:
```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

5. Run the backend server:
```bash
python main.py
```

The backend will run on `http://localhost:8000`

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Trading Signal Logic

The system determines trading signals based on the following rules:

1. **Agreement Cases**:
   - Price ↑ + News Bullish → **BUY** (Strong bullish signal)
   - Price ↓ + News Bearish → **SELL** (Strong bearish signal)

2. **Reversal Cases**:
   - Price ↑ + News Bearish → **BUY** (Bullish reversal - price going up despite bearish news)
   - Price ↓ + News Bullish → **SELL** (Bearish reversal - price going down despite bullish news)

## API Endpoints

- `GET /api/gold/data` - Get all gold price and index data
- `GET /api/gold/data/date/{date}` - Get gold data for a specific date
- `GET /api/gold/signal/{date}` - Get trading signal for a specific date
- `GET /api/gold/news/{date}` - Get news articles for a specific date

## Technologies Used

### Backend
- FastAPI - Modern Python web framework
- Pandas - Data manipulation
- aiohttp - Async HTTP client for web scraping
- BeautifulSoup4 - HTML parsing
- Groq - AI sentiment analysis

### Frontend
- React - UI framework
- Recharts - Charting library
- Axios - HTTP client
- Vite - Build tool
- date-fns - Date utilities

## Notes

- The news scraper searches through multiple pages on investing.com to find articles from the target date
- Sentiment analysis uses Groq's `llama-3.1-8b-instant` model (cheapest option)
- The system includes fallback sentiment analysis using keyword matching if the API fails
- Date format for API calls: `YYYY-MM-DD`

## Future Enhancements

- Support for multiple commodities
- Historical signal backtesting
- Email/SMS alerts for signals
- More sophisticated sentiment analysis
- Integration with trading platforms

