"""
Commodity configuration - defines available commodities and their scrapers
"""
from services.news_scraper import NewsScraper
from services.marketwatch_scraper import MarketWatchScraper

# Scraper cache to avoid re-initializing
_scraper_cache = {}

COMMODITIES = {
    'gold': {
        'name': 'Gold',
        'data_file': 'gold.csv',
        'scraper_type': 'investing',
        'base_url': 'https://www.investing.com/commodities/gold-news'
    },
    'coffee': {
        'name': 'Coffee',
        'data_file': 'coffee.csv',
        'scraper_type': 'marketwatch',
        'search_query': 'coffee',
        'base_url': 'https://www.marketwatch.com/search?q=coffee'
    }
}

def _get_scraper(commodity_key: str):
    """Get or create the scraper for a commodity"""
    if commodity_key not in _scraper_cache:
        config = COMMODITIES[commodity_key]
        scraper_type = config.get('scraper_type', 'investing')
        
        if scraper_type == 'investing':
            _scraper_cache[commodity_key] = NewsScraper()
        elif scraper_type == 'marketwatch':
            search_query = config.get('search_query', commodity_key)
            _scraper_cache[commodity_key] = MarketWatchScraper(search_query=search_query)
        else:
            raise ValueError(f"Unknown scraper type: {scraper_type}")
    
    return _scraper_cache[commodity_key]

def get_commodity_config(commodity: str):
    """Get configuration for a commodity"""
    if commodity not in COMMODITIES:
        raise ValueError(f"Unknown commodity: {commodity}")
    
    config = COMMODITIES[commodity].copy()
    # Add the scraper instance
    config['news_scraper'] = _get_scraper(commodity)
    return config

def get_available_commodities():
    """Get list of available commodities"""
    return list(COMMODITIES.keys())

