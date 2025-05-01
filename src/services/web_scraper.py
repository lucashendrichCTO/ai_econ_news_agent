"""
Web scraper service for the AI Economic Research News Agent.

This module implements the web scraping functionality to fetch articles from various sources.
"""

import time
import requests
import feedparser
from typing import List, Dict, Any
from loguru import logger
from bs4 import BeautifulSoup
from newspaper import Article as NewspaperArticle
from datetime import datetime, timedelta

from src.services.protocols import NewsSourceProtocol, ContentExtractorProtocol
from config.settings import REQUEST_DELAY, MAX_REQUESTS_PER_MINUTE


class WebScraper(NewsSourceProtocol, ContentExtractorProtocol):
    """
    Web scraper for fetching and extracting content from news sources.
    
    Implements the NewsSourceProtocol and ContentExtractorProtocol interfaces.
    """
    
    def __init__(self):
        """Initialize the web scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.last_request_time = 0
    
    def _respect_rate_limits(self):
        """Ensure we respect rate limits for web requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - time_since_last_request)
        
        self.last_request_time = time.time()
    
    def fetch_articles(self, keywords: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch articles based on keywords.
        
        Args:
            keywords: List of keywords to search for
            limit: Maximum number of articles to fetch
            
        Returns:
            List of article data dictionaries
        """
        # This is a generic implementation - in practice, we use fetch_articles_from_source
        # which is tailored to each source type
        raise NotImplementedError("Use fetch_articles_from_source instead")
    
    def fetch_articles_from_source(self, source_config: Dict[str, Any], keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch articles from a specific source based on its configuration.
        
        Args:
            source_config: Source configuration dictionary
            keywords: List of keywords to search for
            
        Returns:
            List of article data dictionaries
        """
        source_type = source_config.get('type', 'website')
        
        if source_type == 'aggregator' and 'rss_url' in source_config:
            return self._fetch_from_rss(source_config['rss_url'], keywords)
        else:
            return self._fetch_from_website(source_config, keywords)
    
    def _fetch_from_rss(self, rss_url: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch articles from an RSS feed.
        
        Args:
            rss_url: URL of the RSS feed
            keywords: List of keywords to filter by
            
        Returns:
            List of article data dictionaries
        """
        self._respect_rate_limits()
        
        try:
            feed = feedparser.parse(rss_url)
            
            articles = []
            for entry in feed.entries:
                # Check if any keyword is in title or description
                title = entry.get('title', '')
                description = entry.get('description', '')
                
                if any(keyword.lower() in title.lower() or keyword.lower() in description.lower() 
                       for keyword in keywords):
                    
                    article = {
                        'title': title,
                        'url': entry.get('link', ''),
                        'published_date': datetime.fromtimestamp(
                            time.mktime(entry.get('published_parsed', time.localtime()))
                        ) if 'published_parsed' in entry else None,
                        'summary': description
                    }
                    
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching from RSS {rss_url}: {str(e)}")
            return []
    
    def _fetch_from_website(self, source_config: Dict[str, Any], keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch articles from a website using its HTML structure.
        
        Args:
            source_config: Source configuration dictionary
            keywords: List of keywords to filter by
            
        Returns:
            List of article data dictionaries
        """
        self._respect_rate_limits()
        
        try:
            url = source_config['url']
            parser_settings = source_config.get('parser_settings', {})
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find article elements based on selector
            article_selector = parser_settings.get('article_selector', 'article')
            article_elements = soup.select(article_selector)
            
            articles = []
            for element in article_elements:
                try:
                    # Extract title
                    title_selector = parser_settings.get('title_selector', 'h2, h3')
                    title_element = element.select_one(title_selector)
                    
                    if not title_element:
                        continue
                    
                    title = title_element.get_text().strip()
                    
                    # Extract URL
                    url_element = title_element.parent if title_element.parent.name == 'a' else title_element.find('a')
                    if not url_element:
                        url_element = element.find('a')
                    
                    if not url_element:
                        continue
                    
                    article_url = url_element.get('href', '')
                    
                    # Handle relative URLs
                    if article_url.startswith('/'):
                        base_url = '/'.join(url.split('/')[:3])  # http(s)://domain.com
                        article_url = base_url + article_url
                    
                    # Check if any keyword is in the title
                    if any(keyword.lower() in title.lower() for keyword in keywords):
                        article = {
                            'title': title,
                            'url': article_url,
                            'source': source_config['name']
                        }
                        
                        articles.append(article)
                
                except Exception as e:
                    logger.debug(f"Error parsing article element: {str(e)}")
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching from website {source_config['name']}: {str(e)}")
            return []
    
    def extract(self, url: str) -> Dict[str, Any]:
        """
        Extract content from a web page.
        
        Args:
            url: URL of the web page
            
        Returns:
            Dictionary containing extracted content
        """
        return self.extract_content(url)
    
    def extract_content(self, url: str, source_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract content from an article URL.
        
        Args:
            url: URL of the article
            source_config: Optional source configuration for custom extraction
            
        Returns:
            Dictionary with extracted content
        """
        self._respect_rate_limits()
        
        try:
            # Use newspaper3k for extraction
            article = NewspaperArticle(url)
            article.download()
            article.parse()
            
            # If source config is provided and has content selector, use it for more precise extraction
            if source_config and 'parser_settings' in source_config:
                try:
                    parser_settings = source_config['parser_settings']
                    content_selector = parser_settings.get('content_selector')
                    
                    if content_selector:
                        response = self.session.get(url, timeout=10)
                        response.raise_for_status()
                        
                        soup = BeautifulSoup(response.text, 'html.parser')
                        content_element = soup.select_one(content_selector)
                        
                        if content_element:
                            # Use the more precise content if available
                            custom_text = content_element.get_text().strip()
                            if len(custom_text) > len(article.text) * 0.5:  # Only use if it's substantial
                                article.text = custom_text
                
                except Exception as e:
                    logger.debug(f"Error with custom content extraction: {str(e)}")
            
            # Extract and format the data
            published_date = article.publish_date
            
            # If no date found, try to find it in meta tags or estimate
            if not published_date:
                # Use current date as fallback
                published_date = datetime.now()
            
            return {
                'title': article.title,
                'text': article.text,
                'html': article.html,
                'authors': article.authors,
                'published_date': published_date,
                'top_image': article.top_image,
                'keywords': article.keywords,
                'summary': article.summary
            }
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            
            # Return minimal content to avoid breaking the pipeline
            return {
                'title': 'Error extracting content',
                'text': f'Failed to extract content from {url}: {str(e)}',
                'html': '',
                'published_date': datetime.now()
            }
