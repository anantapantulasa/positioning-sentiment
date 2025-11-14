import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsScraper:
    BASE_URL = "https://www.investing.com/commodities/gold-news"
    
    async def scrape_news_for_date(self, target_date: datetime) -> List[Dict]:
        """
        Scrape news articles from investing.com for a specific date.
        Uses binary search to quickly find the page range containing target date,
        then does a local crawl to ensure we get all articles.
        """
        logger.info(f"🔍 Starting binary search crawl for date: {target_date.strftime('%Y-%m-%d')}")
        
        target_date_normalized = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        logger.info(f"📅 Target date: {target_date_normalized.date()}")
        
        async with aiohttp.ClientSession() as session:
            # Step 1: Binary search to find approximate page range
            page_range = await self._binary_search_pages(session, target_date_normalized)
            
            if not page_range:
                logger.warning("❌ Could not find target date in available pages")
                return []
            
            start_page, end_page = page_range
            logger.info(f"\n{'='*60}")
            logger.info(f"🎯 Binary search found target date in page range: {start_page} to {end_page}")
            logger.info(f"{'='*60}\n")
            
            # Step 2: Expand the range to catch edge cases
            # Go back one page before start to catch articles at end of previous page
            safe_start = max(1, start_page - 1)
            # Go forward one page after end to ensure completeness
            safe_end = end_page + 1
            
            logger.info(f"📦 Expanding to safe range: {safe_start} to {safe_end} (added buffer pages)")
            
            # Step 3: Crawl the identified range
            all_articles = await self._crawl_page_range(session, safe_start, safe_end)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"📊 Crawling complete. Total articles collected: {len(all_articles)}")
            logger.info(f"{'='*60}\n")
        
        # Step 4: Filter to only articles from the target date
        filtered_articles = []
        for article in all_articles:
            article_date = article.get('date')
            if not article_date:
                continue
            
            article_date_normalized = article_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if article_date_normalized.date() == target_date_normalized.date():
                filtered_articles.append(article)
                logger.debug(f"   ✅ Including: '{article.get('title', '')[:50]}...' ({article_date})")
        
        logger.info(f"✅ Final filtered articles for {target_date_normalized.date()}: {len(filtered_articles)}")
        
        # Sort by date (most recent first)
        filtered_articles.sort(key=lambda x: x['date'], reverse=True)
        
        return filtered_articles
    
    async def _binary_search_pages(self, session: aiohttp.ClientSession, 
                                   target_date: datetime) -> Optional[tuple]:
        """
        Binary search to find the page range containing the target date.
        Returns (start_page, end_page) tuple or None if not found.
        """
        logger.info("\n🔍 Starting binary search to locate target date...")
        
        # First, determine the valid page range
        left = 1
        right = 1000  # Max pages
        
        # Find the actual last page by checking if pages exist
        logger.info("📏 Finding actual last page...")
        actual_last_page = await self._find_last_page(session, right)
        if actual_last_page:
            right = actual_last_page
            logger.info(f"✅ Actual last page: {right}")
        
        # Check if target date is on first page
        first_page_date = await self._get_page_date_range(session, 1)
        if first_page_date:
            earliest, latest = first_page_date
            logger.info(f"📅 Page 1 date range: {earliest.date()} to {latest.date()}")
            if earliest.date() <= target_date.date() <= latest.date():
                logger.info("✅ Target date found on page 1")
                return (1, 1)
            if target_date.date() > latest.date():
                logger.warning(f"⚠️  Target date {target_date.date()} is more recent than page 1 ({latest.date()})")
                return None
        
        # Check if target date is on last page
        last_page_date = await self._get_page_date_range(session, right)
        if last_page_date:
            earliest, latest = last_page_date
            logger.info(f"📅 Page {right} date range: {earliest.date()} to {latest.date()}")
            if target_date.date() < earliest.date():
                logger.warning(f"⚠️  Target date {target_date.date()} is older than page {right} ({earliest.date()})")
                return None
        
        # Binary search for the page containing target date
        first_match_page = None
        last_match_page = None
        
        logger.info(f"\n🔎 Binary searching pages {left} to {right}...")
        
        while left <= right:
            mid = (left + right) // 2
            logger.info(f"\n   Checking page {mid} (range: {left}-{right})")
            
            date_range = await self._get_page_date_range(session, mid)
            if not date_range:
                logger.warning(f"   ⚠️  Could not get date range for page {mid}")
                right = mid - 1
                continue
            
            earliest, latest = date_range
            logger.info(f"   📅 Page {mid} date range: {earliest.date()} to {latest.date()}")
            
            # Check if target date is on this page
            if earliest.date() <= target_date.date() <= latest.date():
                logger.info(f"   ✅ Target date found on page {mid}!")
                # Found a page with target date, but there might be more
                # Record this page and search for boundaries
                if first_match_page is None:
                    first_match_page = mid
                last_match_page = mid
                
                # Search left for first occurrence
                left_boundary = await self._find_first_page_with_date(session, left, mid - 1, target_date)
                # Search right for last occurrence  
                right_boundary = await self._find_last_page_with_date(session, mid + 1, right, target_date)
                
                if left_boundary is not None:
                    first_match_page = left_boundary
                if right_boundary is not None:
                    last_match_page = right_boundary
                
                return (first_match_page, last_match_page)
            
            elif target_date.date() > latest.date():
                # Target is more recent, search earlier pages (lower page numbers)
                logger.info(f"   ⬅️  Target date is more recent, searching pages {left}-{mid-1}")
                right = mid - 1
            else:
                # Target is older, search later pages (higher page numbers)
                logger.info(f"   ➡️  Target date is older, searching pages {mid+1}-{right}")
                left = mid + 1
        
        return None
    
    async def _find_first_page_with_date(self, session: aiohttp.ClientSession,
                                        left: int, right: int, target_date: datetime) -> Optional[int]:
        """Find the first (leftmost) page containing target date"""
        if left > right:
            return None
        
        first_page = None
        while left <= right:
            mid = (left + right) // 2
            date_range = await self._get_page_date_range(session, mid)
            if not date_range:
                right = mid - 1
                continue
            
            earliest, latest = date_range
            if earliest.date() <= target_date.date() <= latest.date():
                first_page = mid
                right = mid - 1  # Keep searching left
            elif target_date.date() > latest.date():
                right = mid - 1
            else:
                left = mid + 1
        
        return first_page
    
    async def _find_last_page_with_date(self, session: aiohttp.ClientSession,
                                       left: int, right: int, target_date: datetime) -> Optional[int]:
        """Find the last (rightmost) page containing target date"""
        if left > right:
            return None
        
        last_page = None
        while left <= right:
            mid = (left + right) // 2
            date_range = await self._get_page_date_range(session, mid)
            if not date_range:
                right = mid - 1
                continue
            
            earliest, latest = date_range
            if earliest.date() <= target_date.date() <= latest.date():
                last_page = mid
                left = mid + 1  # Keep searching right
            elif target_date.date() > latest.date():
                right = mid - 1
            else:
                left = mid + 1
        
        return last_page
    
    async def _find_last_page(self, session: aiohttp.ClientSession, max_page: int) -> Optional[int]:
        """Find the actual last page by binary searching for 404s"""
        left = 1
        right = max_page
        last_valid = 1
        
        while left <= right:
            mid = (left + right) // 2
            exists = await self._page_exists(session, mid)
            
            if exists:
                last_valid = mid
                left = mid + 1
            else:
                right = mid - 1
        
        return last_valid
    
    async def _page_exists(self, session: aiohttp.ClientSession, page: int) -> bool:
        """Check if a page exists (returns True if status is 200)"""
        if page == 1:
            page_url = self.BASE_URL
        else:
            page_url = f"{self.BASE_URL}/{page}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            async with session.head(page_url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                return response.status == 200
        except:
            return False
    
    async def _get_page_date_range(self, session: aiohttp.ClientSession, 
                                   page: int) -> Optional[tuple]:
        """
        Get the earliest and latest article dates on a page.
        Returns (earliest_date, latest_date) tuple or None if page can't be fetched.
        """
        if page == 1:
            page_url = self.BASE_URL
        else:
            page_url = f"{self.BASE_URL}/{page}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with session.get(page_url, headers=headers, 
                                 timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                articles = self._parse_news_page(html)
                
                if not articles:
                    return None
                
                dates = [a['date'] for a in articles if a.get('date')]
                if not dates:
                    return None
                
                earliest = min(dates).replace(hour=0, minute=0, second=0, microsecond=0)
                latest = max(dates).replace(hour=0, minute=0, second=0, microsecond=0)
                
                return (earliest, latest)
        
        except Exception as e:
            logger.error(f"   Error getting date range for page {page}: {e}")
            return None
    
    async def _crawl_page_range(self, session: aiohttp.ClientSession, 
                               start_page: int, end_page: int) -> List[Dict]:
        """Crawl all pages in the specified range and collect articles"""
        logger.info(f"\n📚 Crawling pages {start_page} to {end_page}...")
        
        all_articles = []
        
        for page in range(start_page, end_page + 1):
            if page == 1:
                page_url = self.BASE_URL
            else:
                page_url = f"{self.BASE_URL}/{page}"
            
            logger.info(f"\n📄 Fetching page {page}: {page_url}")
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.get(page_url, headers=headers, 
                                     timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        logger.warning(f"   ⚠️  Status {response.status}")
                        continue
                    
                    html = await response.text()
                    articles = self._parse_news_page(html)
                    
                    logger.info(f"   ✅ Found {len(articles)} articles on page {page}")
                    
                    for article in articles:
                        article_date = article.get('date')
                        if article_date:
                            logger.info(f"      📰 '{article['title'][:50]}...' - {article_date.date()}")
                    
                    all_articles.extend(articles)
                
                # Be polite
                await asyncio.sleep(0.5)
            
            except Exception as e:
                logger.error(f"   ❌ Error fetching page {page}: {e}")
                continue
        
        return all_articles
    
    async def scrape_full_article(self, article_url: str) -> Optional[Dict]:
        """
        Scrape the full content of an article page.
        Returns dict with full_text, author, and other metadata.
        """
        logger.info(f"📖 Fetching full article: {article_url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(article_url, headers=headers, 
                                     timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status != 200:
                        logger.warning(f"   ⚠️  Status {response.status} for {article_url}")
                        return None
                    
                    html = await response.text()
                    return self._parse_article_page(html, article_url)
        
        except Exception as e:
            logger.error(f"   ❌ Error fetching article {article_url}: {e}")
            return None
    
    def _parse_article_page(self, html: str, article_url: str) -> Optional[Dict]:
        """Parse the full article page and extract content"""
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # Find the article container
            article_container = soup.find('div', id='article')
            if not article_container:
                logger.warning("   ⚠️  Could not find article container (div#article)")
                return None
            
            # Find the main content div with article text
            # Based on the HTML: <div class="article_WYSIWYG__O0uhw article_articlePage__UM23q">
            content_div = article_container.find('div', class_=lambda x: x and 'article_WYSIWYG' in str(x))
            
            if not content_div:
                # Try alternative selector
                content_div = article_container.find('div', class_=lambda x: x and 'articlePage' in str(x))
            
            if not content_div:
                logger.warning("   ⚠️  Could not find article content div")
                return None
            
            # Extract all paragraph text
            paragraphs = content_div.find_all('p')
            
            if not paragraphs:
                logger.warning("   ⚠️  No paragraphs found in article")
                return None
            
            # First paragraph might be the author (e.g., "By Sinéad Carew and Dhara Ranasinghe")
            author = None
            article_paragraphs = []
            
            for i, p in enumerate(paragraphs):
                text = p.get_text(strip=True)
                
                # Skip empty paragraphs
                if not text:
                    continue
                
                # Check if first paragraph is author line
                if i == 0 and text.startswith('By '):
                    author = text.replace('By ', '').strip()
                    logger.debug(f"   👤 Author: {author}")
                    continue
                
                # Skip advertisement divs or very short paragraphs that might be ads
                if len(text) < 20:
                    continue
                
                article_paragraphs.append(text)
            
            # Join all paragraphs into full text
            full_text = '\n\n'.join(article_paragraphs)
            
            logger.info(f"   ✅ Extracted {len(article_paragraphs)} paragraphs ({len(full_text)} characters)")
            
            return {
                'full_text': full_text,
                'author': author,
                'paragraph_count': len(article_paragraphs),
                'character_count': len(full_text),
                'url': article_url
            }
        
        except Exception as e:
            logger.error(f"   ❌ Error parsing article page: {e}")
            return None
    
    async def scrape_articles_with_content(self, target_date: datetime, 
                                          fetch_full_content: bool = True) -> List[Dict]:
        """
        Scrape articles for a target date and optionally fetch full content.
        
        Args:
            target_date: Date to scrape articles for
            fetch_full_content: If True, fetch full article content for each article
        
        Returns:
            List of article dictionaries with full content if requested
        """
        # First, get all articles from the listing pages
        articles = await self.scrape_news_for_date(target_date)
        
        if not fetch_full_content:
            return articles
        
        # Now fetch full content for each article
        logger.info(f"\n{'='*60}")
        logger.info(f"📚 Fetching full content for {len(articles)} articles...")
        logger.info(f"{'='*60}\n")
        
        for i, article in enumerate(articles, 1):
            logger.info(f"\n[{i}/{len(articles)}] Fetching: {article['title'][:50]}...")
            
            full_content = await self.scrape_full_article(article['link'])
            
            if full_content:
                article['full_content'] = full_content['full_text']
                article['author'] = full_content['author']
                article['paragraph_count'] = full_content['paragraph_count']
                article['character_count'] = full_content['character_count']
                logger.info(f"   ✅ Got {full_content['paragraph_count']} paragraphs, {full_content['character_count']} chars")
            else:
                article['full_content'] = None
                article['author'] = None
                logger.warning(f"   ⚠️  Failed to fetch full content")
            
            # Be polite - add delay between article requests
            await asyncio.sleep(1)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Completed fetching full content for all articles")
        logger.info(f"{'='*60}\n")
        
        return articles
    
    def _parse_news_page(self, html: str) -> List[Dict]:
        """Parse HTML and extract news articles"""
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # Find article containers using the exact selector from the HTML
        article_elements = soup.find_all('article', attrs={'data-test': 'article-item'})
        
        for idx, article_elem in enumerate(article_elements):
            try:
                # Extract title and link
                title_link = article_elem.find('a', attrs={'data-test': 'article-title-link'})
                if not title_link:
                    continue
                
                title = title_link.get_text(strip=True)
                link = title_link.get('href', '')
                
                # Make link absolute if it's relative
                if link and not link.startswith('http'):
                    link = f"https://www.investing.com{link}"
                
                if not title or len(title) < 10:
                    continue
                
                # Extract date from <time> element
                time_elem = article_elem.find('time', attrs={'data-test': 'article-publish-date'})
                if not time_elem:
                    continue
                
                datetime_attr = time_elem.get('datetime')
                if not datetime_attr:
                    continue
                
                article_date = self._parse_datetime(datetime_attr)
                if not article_date:
                    continue
                
                # Extract description
                description_elem = article_elem.find('p', attrs={'data-test': 'article-description'})
                description = description_elem.get_text(strip=True) if description_elem else ""
                
                # Get the display text
                display_date = time_elem.get_text(strip=True)
                
                articles.append({
                    'title': title,
                    'link': link,
                    'date': article_date,
                    'summary': description,
                    'display_date': display_date,
                    'raw_datetime': datetime_attr
                })
                
            except Exception as e:
                logger.debug(f"   Error parsing article {idx+1}: {e}")
                continue
        
        return articles
    
    def _parse_datetime(self, datetime_str: str) -> datetime:
        """Parse datetime string from the datetime attribute"""
        try:
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%SZ",
            ]
            
            for fmt in formats:
                try:
                    parsed = datetime.strptime(datetime_str, fmt)
                    return parsed
                except ValueError:
                    continue
            
            return None
            
        except Exception as e:
            return None


# Example usage
async def main():
    scraper = NewsScraper()
    
    # Test 1: Scrape article listings only (no full content)
    print(f"\n{'='*70}")
    print(f"TEST 1: Scraping article LISTINGS for TODAY (no full content)")
    print(f"{'='*70}\n")
    
    today = datetime.now()
    articles_today = await scraper.scrape_news_for_date(today)
    
    print(f"\n{'='*70}")
    print(f"RESULTS: Found {len(articles_today)} articles for {today.strftime('%Y-%m-%d')}")
    print(f"{'='*70}\n")
    
    for i, article in enumerate(articles_today[:3], 1):
        print(f"{i}. {article['title']}")
        print(f"   Date: {article['date']} (Display: {article['display_date']})")
        print(f"   Link: {article['link']}")
        if article['summary']:
            print(f"   Summary: {article['summary'][:100]}...")
        print()
    
    if len(articles_today) > 3:
        print(f"   ... and {len(articles_today) - 3} more articles\n")
    
    # Test 2: Scrape WITH full article content
    print(f"\n{'='*70}")
    print(f"TEST 2: Scraping articles WITH FULL CONTENT for Nov 12, 2025")
    print(f"{'='*70}\n")
    
    target_date = datetime(2025, 11, 12)
    articles_with_content = await scraper.scrape_articles_with_content(
        target_date, 
        fetch_full_content=True
    )
    
    print(f"\n{'='*70}")
    print(f"RESULTS: Found {len(articles_with_content)} articles with full content")
    print(f"{'='*70}\n")
    
    for i, article in enumerate(articles_with_content[:2], 1):  # Show first 2
        print(f"{i}. {article['title']}")
        print(f"   Date: {article['date']}")
        print(f"   Link: {article['link']}")
        if article.get('author'):
            print(f"   Author: {article['author']}")
        if article.get('full_content'):
            print(f"   Full Content ({article.get('character_count', 0)} chars):")
            # Show first 300 characters of full content
            print(f"   {article['full_content'][:300]}...")
        else:
            print(f"   ⚠️  Full content not available")
        print()
    
    if len(articles_with_content) > 2:
        print(f"   ... and {len(articles_with_content) - 2} more articles\n")


if __name__ == "__main__":
    asyncio.run(main())
