import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
import logging
import re
from urllib.parse import urlencode

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketWatchScraper:
    BASE_SEARCH_URL = "https://www.marketwatch.com/search"
    
    def __init__(self, search_query: str = "coffee"):
        self.search_query = search_query
    
    async def scrape_news_for_date(self, target_date: datetime) -> List[Dict]:
        """
        Scrape news articles for a specific date.
        
        Args:
            target_date: Target date to find articles for
        
        Returns:
            List of article dictionaries matching the target date
        """
        logger.info(f"🔍 Starting MarketWatch scrape for query: '{self.search_query}' and date: {target_date.strftime('%Y-%m-%d')}")
        
        # Get all articles
        all_articles = await self.scrape_news(max_articles=100)
        
        # Filter articles by target date
        target_date_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        target_date_end = target_date_start + timedelta(days=1)
        
        filtered_articles = []
        for article in all_articles:
            article_date = article.get('date')
            if article_date:
                # Normalize dates to date-only for comparison
                article_date_normalized = article_date.replace(hour=0, minute=0, second=0, microsecond=0)
                if target_date_start <= article_date_normalized < target_date_end:
                    filtered_articles.append(article)
        
        logger.info(f"✅ Found {len(filtered_articles)} articles for date {target_date.strftime('%Y-%m-%d')}")
        return filtered_articles[:20]  # Limit to 20 most relevant articles
    
    async def scrape_news(self, max_articles: int = 50) -> List[Dict]:
        """
        Scrape news articles from MarketWatch search results.
        
        Args:
            max_articles: Maximum number of articles to return
        
        Returns:
            List of article dictionaries with metadata and content
        """
        logger.info(f"🔍 Starting MarketWatch scrape for query: '{self.search_query}'")
        
        articles = []
        
        async with aiohttp.ClientSession() as session:
            # MarketWatch search seems to load results dynamically
            # We'll start with page 1 and see what we can get
            articles = await self._scrape_search_page(session)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"📊 Found {len(articles)} articles")
            logger.info(f"{'='*60}\n")
        
        # Limit to max_articles
        articles = articles[:max_articles]
        
        return articles
    
    async def scrape_with_full_content(self, max_articles: int = 20) -> List[Dict]:
        """
        Scrape articles and fetch full content for each.
        
        Args:
            max_articles: Maximum number of articles to fetch full content for
        
        Returns:
            List of article dictionaries with full content
        """
        # First get article listings
        articles = await self.scrape_news(max_articles)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📚 Fetching full content for {len(articles)} articles...")
        logger.info(f"{'='*60}\n")
        
        async with aiohttp.ClientSession() as session:
            for i, article in enumerate(articles, 1):
                logger.info(f"\n[{i}/{len(articles)}] Fetching: {article['title'][:50]}...")
                
                full_content = await self._scrape_full_article(session, article['link'])
                
                if full_content:
                    article['full_content'] = full_content['full_text']
                    article['paragraph_count'] = full_content['paragraph_count']
                    article['character_count'] = full_content['character_count']
                    logger.info(f"   ✅ Got {full_content['paragraph_count']} paragraphs, {full_content['character_count']} chars")
                else:
                    article['full_content'] = None
                    article['paragraph_count'] = 0
                    article['character_count'] = 0
                    logger.warning(f"   ⚠️  Could not fetch full content (possibly paywalled)")
                
                # Be polite
                await asyncio.sleep(1)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Completed fetching full content")
        logger.info(f"{'='*60}\n")
        
        return articles
    
    async def _scrape_search_page(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Scrape the search results page"""
        # Build search URL
        params = {
            'q': self.search_query,
            'ts': '0',
            'tab': 'All News'
        }
        search_url = f"{self.BASE_SEARCH_URL}?{urlencode(params)}"
        
        logger.info(f"📄 Fetching search page: {search_url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            async with session.get(search_url, headers=headers, 
                                 timeout=aiohttp.ClientTimeout(total=15)) as response:
                logger.info(f"   Status code: {response.status}")
                
                if response.status != 200:
                    logger.warning(f"   ⚠️  Non-200 status code: {response.status}")
                    return []
                
                html = await response.text()
                logger.info(f"   HTML length: {len(html)} characters")
                
                articles = self._parse_search_results(html)
                logger.info(f"   ✅ Found {len(articles)} articles")
                
                return articles
        
        except Exception as e:
            logger.error(f"   ❌ Error fetching search page: {e}")
            return []
    
    def _parse_search_results(self, html: str) -> List[Dict]:
        """Parse search results HTML and extract article metadata"""
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        logger.debug("   🔍 Parsing search results...")
        
        # Find article elements: <div class="element element--article">
        article_elements = soup.find_all('div', class_=lambda x: x and 'element--article' in str(x))
        
        logger.info(f"   📝 Found {len(article_elements)} article elements")
        
        for idx, article_elem in enumerate(article_elements):
            try:
                # Extract headline and link
                # <h3 class="article__headline"><a class="link" href="...">
                headline_elem = article_elem.find('h3', class_=lambda x: x and 'article__headline' in str(x))
                if not headline_elem:
                    logger.debug(f"   ⏭️  Article {idx+1}: No headline found")
                    continue
                
                link_elem = headline_elem.find('a', class_='link')
                if not link_elem:
                    logger.debug(f"   ⏭️  Article {idx+1}: No link found")
                    continue
                
                title = link_elem.get_text(strip=True)
                link = link_elem.get('href', '')
                
                # Make link absolute if needed
                if link and not link.startswith('http'):
                    link = f"https://www.marketwatch.com{link}"
                
                if not title or len(title) < 10:
                    logger.debug(f"   ⏭️  Article {idx+1}: Title too short")
                    continue
                
                # Extract timestamp
                # <span class="article__timestamp">
                timestamp_elem = article_elem.find('span', class_=lambda x: x and 'article__timestamp' in str(x))
                timestamp_text = timestamp_elem.get_text(strip=True) if timestamp_elem else None
                
                # Parse timestamp
                article_date = self._parse_timestamp(timestamp_text) if timestamp_text else None
                
                # Extract author
                # <span class="article__author">
                author_elem = article_elem.find('span', class_=lambda x: x and 'article__author' in str(x))
                author = author_elem.get_text(strip=True) if author_elem else None
                
                # Clean up author (remove "by " prefix if present)
                if author and author.lower().startswith('by '):
                    author = author[3:].strip()
                
                articles.append({
                    'title': title,
                    'link': link,
                    'date': article_date,
                    'timestamp_text': timestamp_text,
                    'author': author,
                    'source': 'MarketWatch',
                    'search_query': self.search_query
                })
                
                logger.info(f"   ✅ Article {idx+1}: '{title[:50]}...'")
                logger.info(f"      Date: {article_date if article_date else timestamp_text}")
                logger.info(f"      Author: {author if author else 'Unknown'}")
                
            except Exception as e:
                logger.error(f"   ❌ Error parsing article {idx+1}: {e}")
                continue
        
        return articles
    
    def _parse_timestamp(self, timestamp_text: str) -> Optional[datetime]:
        """Parse timestamp text into datetime object"""
        if not timestamp_text:
            return None
        
        try:
            now = datetime.now()
            text_lower = timestamp_text.strip().lower()
            
            # Handle relative times like "13 minutes ago", "2 hours ago"
            relative_pattern = r'(\d+)\s+(minute|minutes|hour|hours|day|days)\s+ago'
            match = re.search(relative_pattern, text_lower)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                
                if 'minute' in unit:
                    return now - timedelta(minutes=amount)
                elif 'hour' in unit:
                    return now - timedelta(hours=amount)
                elif 'day' in unit:
                    return now - timedelta(days=amount)
            
            # Handle absolute dates like "Nov. 13, 2025 at 5:37 p.m. ET" or "Nov. 12, 2025"
            # Try various date formats - prioritize simple date formats first (most common in MarketWatch)
            formats = [
                "%b. %d, %Y",              # Nov. 12, 2025 (with period - MarketWatch format, most common)
                "%b %d, %Y",               # Nov 12, 2025 (without period)
                "%B %d, %Y",               # November 12, 2025
                "%b. %d, %Y at %I:%M %p",  # Nov. 13, 2025 at 5:37 p.m.
                "%b %d, %Y at %I:%M %p",   # Nov 13, 2025 at 5:37 p.m.
                "%B %d, %Y at %I:%M %p",   # November 13, 2025 at 5:37 p.m.
                "%Y-%m-%d",                # 2025-11-13
            ]
            
            # Clean up timestamp text (remove timezone info like "ET" and "at" time parts)
            # First remove timezone
            clean_text = re.sub(r'\s+(ET|EST|EDT|PT|PST|PDT)$', '', timestamp_text.strip())
            # Remove "at HH:MM AM/PM" if present (we'll try formats with and without time)
            clean_text_no_time = re.sub(r'\s+at\s+\d+:\d+\s+[ap]\.?m\.?', '', clean_text, flags=re.IGNORECASE)
            
            # Try formats with original text first (in case it has time), then without time
            for text_to_parse in [clean_text, clean_text_no_time]:
                for fmt in formats:
                    try:
                        parsed = datetime.strptime(text_to_parse, fmt)
                        return parsed
                    except ValueError:
                        continue
            
            logger.debug(f"      Could not parse timestamp: '{timestamp_text}'")
            return None
            
        except Exception as e:
            logger.debug(f"      Error parsing timestamp '{timestamp_text}': {e}")
            return None
    
    async def _scrape_full_article(self, session: aiohttp.ClientSession, 
                                   article_url: str) -> Optional[Dict]:
        """
        Scrape full article content from an article page.
        Note: Some articles may be paywalled.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            async with session.get(article_url, headers=headers, 
                                 timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status != 200:
                    logger.warning(f"   ⚠️  Status {response.status}")
                    return None
                
                html = await response.text()
                return self._parse_article_page(html, article_url)
        
        except Exception as e:
            logger.error(f"   ❌ Error fetching article: {e}")
            return None
    
    def _parse_article_page(self, html: str, article_url: str) -> Optional[Dict]:
        """Parse the full article page and extract content"""
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # Find the main article content section
            # <section class="ef4qpkp0 css-1c7nx44-Container">
            content_section = soup.find('section', class_=lambda x: x and 'Container' in str(x))
            
            if not content_section:
                # Try alternative selectors
                content_section = soup.find('div', id='maincontent')
            
            if not content_section:
                logger.warning("   ⚠️  Could not find article content section")
                return None
            
            # Find all paragraphs
            # <p class="e1bc1vag0 css-1dqcy4b-StyledNewsKitParagraph" data-type="paragraph">
            paragraphs = content_section.find_all('p', attrs={'data-type': 'paragraph'})
            
            if not paragraphs:
                # Try finding any <p> tags
                paragraphs = content_section.find_all('p')
            
            if not paragraphs:
                logger.warning("   ⚠️  No paragraphs found in article")
                return None
            
            # Extract text from paragraphs
            article_paragraphs = []
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                
                # Skip empty paragraphs
                if not text or len(text) < 20:
                    continue
                
                # Skip obvious ads or disclaimers
                if any(keyword in text.lower() for keyword in ['advertisement', 'subscribe now', 'sign up']):
                    continue
                
                article_paragraphs.append(text)
            
            if not article_paragraphs:
                logger.warning("   ⚠️  No valid paragraphs extracted")
                return None
            
            # Join all paragraphs
            full_text = '\n\n'.join(article_paragraphs)
            
            logger.debug(f"   ✅ Extracted {len(article_paragraphs)} paragraphs ({len(full_text)} chars)")
            
            return {
                'full_text': full_text,
                'paragraph_count': len(article_paragraphs),
                'character_count': len(full_text),
                'url': article_url
            }
        
        except Exception as e:
            logger.error(f"   ❌ Error parsing article page: {e}")
            return None


# Example usage
async def main():
    # Create scraper for coffee news
    scraper = MarketWatchScraper(search_query="coffee")
    
    # Test 1: Get article listings only
    print(f"\n{'='*70}")
    print(f"TEST 1: Scraping MarketWatch for 'coffee' articles (listings only)")
    print(f"{'='*70}\n")
    
    articles = await scraper.scrape_news(max_articles=30)
    
    print(f"\n{'='*70}")
    print(f"RESULTS: Found {len(articles)} articles")
    print(f"{'='*70}\n")
    
    for i, article in enumerate(articles[:5], 1):
        print(f"{i}. {article['title']}")
        print(f"   Date: {article['date'] if article['date'] else article['timestamp_text']}")
        print(f"   Author: {article['author'] if article['author'] else 'Unknown'}")
        print(f"   Link: {article['link']}")
        print()
    
    if len(articles) > 5:
        print(f"   ... and {len(articles) - 5} more articles\n")
    
    # Test 2: Get articles with full content
    print(f"\n{'='*70}")
    print(f"TEST 2: Scraping with FULL CONTENT (first 3 articles)")
    print(f"{'='*70}\n")
    
    articles_with_content = await scraper.scrape_with_full_content(max_articles=3)
    
    print(f"\n{'='*70}")
    print(f"RESULTS: Fetched full content for {len(articles_with_content)} articles")
    print(f"{'='*70}\n")
    
    for i, article in enumerate(articles_with_content, 1):
        print(f"{i}. {article['title']}")
        print(f"   Author: {article['author'] if article['author'] else 'Unknown'}")
        print(f"   Link: {article['link']}")
        
        if article.get('full_content'):
            print(f"   Full Content ({article['character_count']} chars, {article['paragraph_count']} paragraphs):")
            print(f"   {article['full_content'][:300]}...")
        else:
            print(f"   ⚠️  Full content not available (possibly paywalled)")
        print()


if __name__ == "__main__":
    asyncio.run(main())
