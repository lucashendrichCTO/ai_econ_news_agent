"""
Link checker utility for AI Economic News Agent
Verifies that article links are accessible before displaying them
"""

import requests
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Constants
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 2
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
MAX_WORKERS = 5  # Maximum number of concurrent link checks

def check_link(url: str) -> Tuple[str, bool, Optional[str]]:
    """
    Check if a URL is accessible
    
    Args:
        url: The URL to check
        
    Returns:
        Tuple containing (url, is_valid, error_message)
    """
    headers = {
        'User-Agent': USER_AGENT
    }
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.head(url, timeout=REQUEST_TIMEOUT, headers=headers, allow_redirects=True)
            
            # If head request fails, try a get request with stream=True to avoid downloading the entire content
            if response.status_code >= 400:
                response = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers, stream=True, allow_redirects=True)
                
            if response.status_code < 400:
                return url, True, None
            else:
                return url, False, f"HTTP status code: {response.status_code}"
                
        except requests.RequestException as e:
            if attempt < MAX_RETRIES:
                time.sleep(1)  # Wait before retrying
                continue
            return url, False, str(e)
    
    return url, False, "Max retries exceeded"

def verify_article_links(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Verify all article links and filter out invalid ones
    
    Args:
        articles: List of article dictionaries
        
    Returns:
        List of articles with valid links
    """
    urls_to_check = [(article['id'], article['url']) for article in articles]
    valid_articles = []
    results = {}
    
    logging.info(f"Checking {len(urls_to_check)} article links...")
    
    # Check links in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_link, url): (article_id, url) for article_id, url in urls_to_check}
        
        for future in futures:
            article_id, url = futures[future]
            try:
                url, is_valid, error = future.result()
                results[article_id] = (is_valid, error)
                
                if is_valid:
                    logging.info(f"Valid link: {url}")
                else:
                    logging.warning(f"Invalid link: {url} - {error}")
            except Exception as e:
                logging.error(f"Error checking link {url}: {str(e)}")
                results[article_id] = (False, str(e))
    
    # Filter articles based on link validity
    for article in articles:
        is_valid, error = results.get(article['id'], (False, "Link not checked"))
        if is_valid:
            valid_articles.append(article)
        else:
            logging.warning(f"Removing article '{article['title']}' due to invalid link: {error}")
    
    logging.info(f"Found {len(valid_articles)} articles with valid links out of {len(articles)}")
    return valid_articles

if __name__ == "__main__":
    # Example usage
    test_articles = [
        {
            'id': 'test-1',
            'title': 'Test Article 1',
            'url': 'https://www.google.com',
            'relevance_score': 0.95
        },
        {
            'id': 'test-2',
            'title': 'Test Article 2',
            'url': 'https://this-url-does-not-exist-123456789.com',
            'relevance_score': 0.90
        }
    ]
    
    valid_articles = verify_article_links(test_articles)
    print(f"Valid articles: {len(valid_articles)}")
    for article in valid_articles:
        print(f"- {article['title']}: {article['url']}")
