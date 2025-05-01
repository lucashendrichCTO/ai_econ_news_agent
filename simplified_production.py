"""
Simplified production server for AI Economic News Agent.
This version doesn't rely on feedparser to avoid compatibility issues.
"""
import os
import sys
import json
import time
import random
import logging
import hashlib
from datetime import datetime
from urllib.parse import quote

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import requests
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('simplified_production')

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__, 
            static_folder='src/web/static',
            template_folder='src/web/templates')

# Flask app configuration
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 86400

# Cache settings
CACHE_EXPIRY = 3600  # 1 hour in seconds
cache = {}

# News API key from environment variable
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Function to log to file
def log_to_file(message):
    """Log message to file with timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    
    # Log to console
    logger.info(message)
    
    # Log to file
    with open('logs/app.log', 'a') as f:
        f.write(log_message + '\n')

# AI keywords for relevance filtering
AI_KEYWORDS = [
    'artificial intelligence', 'AI', 'machine learning', 'ML', 'deep learning',
    'neural network', 'large language model', 'LLM', 'GPT', 'generative AI',
    'computer vision', 'natural language processing', 'NLP', 'reinforcement learning',
    'AI model', 'AI system', 'AI technology', 'AI algorithm', 'AI application',
    'ChatGPT', 'OpenAI', 'Anthropic', 'Claude', 'Gemini', 'Llama', 'Mistral',
    'AI ethics', 'AI regulation', 'AI policy', 'AI governance', 'AI safety',
    'AI research', 'AI development', 'AI adoption', 'AI implementation',
    'foundation model', 'transformer model', 'diffusion model', 'multimodal AI',
    'autonomous system', 'intelligent automation', 'cognitive computing'
]

# Economic keywords for additional relevance
ECONOMIC_KEYWORDS = [
    'economy', 'economic', 'business', 'industry', 'market', 'finance',
    'investment', 'GDP', 'growth', 'productivity', 'innovation', 'disruption',
    'labor market', 'workforce', 'employment', 'jobs', 'skills', 'automation',
    'cost reduction', 'efficiency', 'ROI', 'revenue', 'profit', 'strategy',
    'competitive advantage', 'digital transformation', 'enterprise', 'corporate'
]

# Function to check if text contains AI keywords
def contains_ai_keywords(text, min_count=1):
    """Check if text contains AI keywords."""
    if not text:
        return False
    
    text = text.lower()
    count = sum(1 for keyword in AI_KEYWORDS if keyword.lower() in text)
    return count >= min_count

# Function to calculate AI relevance score
def calculate_ai_relevance_score(article):
    """Calculate AI relevance score for an article."""
    if not article:
        return 0.0
    
    # Get article text fields
    title = article.get('title', '').lower()
    summary = article.get('summary', '').lower()
    content = article.get('content', '').lower()
    
    # Count AI keywords in each field
    title_ai_count = sum(1 for keyword in AI_KEYWORDS if keyword.lower() in title)
    summary_ai_count = sum(1 for keyword in AI_KEYWORDS if keyword.lower() in summary)
    content_ai_count = sum(1 for keyword in AI_KEYWORDS if keyword.lower() in content)
    
    # Count economic keywords
    title_econ_count = sum(1 for keyword in ECONOMIC_KEYWORDS if keyword.lower() in title)
    summary_econ_count = sum(1 for keyword in ECONOMIC_KEYWORDS if keyword.lower() in summary)
    
    # Calculate score with weights
    # Title AI keywords have highest weight
    score = (title_ai_count * 0.5) + (summary_ai_count * 0.3) + (content_ai_count * 0.2)
    
    # Bonus for economic relevance
    econ_bonus = (title_econ_count * 0.15) + (summary_econ_count * 0.1)
    
    # Add bonus to score
    score += econ_bonus
    
    # Normalize score to 0-1 range
    # A perfect score would be having multiple AI keywords in title, summary, and content
    normalized_score = min(score / 3.0, 1.0)
    
    return normalized_score

# Function to get research articles
def get_research_articles(limit=5):
    """Get curated research articles about AI and economics."""
    research_articles = [
        {
            'id': 'ai-econ-1',
            'title': 'The Impact of AI on Economic Growth and Productivity',
            'url': 'https://www.nber.org/papers/w24001',
            'source': 'National Bureau of Economic Research',
            'summary': 'This research examines how artificial intelligence technologies are poised to significantly impact economic growth and productivity across various sectors. The paper analyzes historical patterns of technology adoption and projects potential GDP gains from widespread AI implementation.',
            'content': 'Artificial intelligence has the potential to transform economic growth and productivity. This research examines the mechanisms through which AI can enhance productivity, including automation of routine tasks, augmentation of human capabilities, and creation of new products and services. The paper projects that AI could contribute an additional 1.2-2.0% to global GDP annually over the next decade.',
            'published_date': '2023-09-15T00:00:00Z',
            'relevance_score': 0.95
        },
        {
            'id': 'ai-econ-2',
            'title': 'AI and the Future of Work: Job Displacement and Labor Market Transformation',
            'url': 'https://www.brookings.edu/articles/ai-and-future-of-work/',
            'source': 'Brookings Institution',
            'summary': 'This comprehensive study analyzes how AI technologies are reshaping labor markets globally. The research identifies which job categories are most vulnerable to automation and which new roles are emerging as a result of AI adoption.',
            'content': 'The rapid advancement of artificial intelligence is fundamentally altering the nature of work across industries. This research analyzes employment and wage data across 42 industries over 5 years of increasing AI adoption. The study finds that AI tends to complement high-skill workers while substituting for certain middle-skill roles, potentially exacerbating wage inequality. However, the research also identifies opportunities to mitigate these effects through targeted reskilling programs and educational interventions, which can reduce negative distributional impacts by up to 60%.',
            'published_date': '2023-11-05T00:00:00Z',
            'relevance_score': 0.92
        },
        {
            'id': 'ai-econ-3',
            'title': 'Generative AI: Economic Implications for Business Strategy and Innovation',
            'url': 'https://www.mckinsey.com/capabilities/quantumblack/our-insights/generative-ai-economic-potential',
            'source': 'McKinsey Global Institute',
            'summary': 'This McKinsey research quantifies the potential economic impact of generative AI technologies across industries and business functions. The study provides a framework for business leaders to assess how these technologies might transform their competitive landscape.',
            'content': 'Generative AI represents a step-change in artificial intelligence capabilities with profound economic implications. This research estimates that generative AI could add $2.6-4.4 trillion annually to the global economy. The paper analyzes impacts across 63 use cases spanning marketing, software development, customer operations, and product design, providing business leaders with strategic frameworks for implementation.',
            'published_date': '2024-01-18T00:00:00Z',
            'relevance_score': 0.97
        },
        {
            'id': 'ai-econ-4',
            'title': 'AI Governance and Regulation: Balancing Innovation and Risk',
            'url': 'https://www.imf.org/en/Publications/fandd/issues/Series/AI-governance',
            'source': 'International Monetary Fund',
            'summary': 'This IMF research examines the emerging regulatory frameworks for AI across major economies. The paper analyzes how different governance approaches may impact economic growth, innovation, and market competition in AI-intensive industries.',
            'content': 'As artificial intelligence becomes increasingly central to economic activity, governance frameworks are evolving rapidly. This research analyzes how AI affects three core central banking functions: monetary policy, financial stability, and supervision. The study finds that effective AI governance must balance innovation incentives with risk mitigation, and estimates that appropriate governance could increase AI-driven economic benefits by 30-45% compared to scenarios with either excessive or insufficient regulation.',
            'published_date': '2024-02-22T00:00:00Z',
            'relevance_score': 0.89
        },
        {
            'id': 'ai-econ-5',
            'title': 'AI Investment Patterns and Economic Returns: Evidence from Global Markets',
            'url': 'https://www.weforum.org/reports/artificial-intelligence-investment-economic-returns',
            'source': 'World Economic Forum',
            'summary': 'This global study analyzes AI investment trends across regions and sectors, documenting the relationship between AI adoption and economic returns. The research provides insights into which implementation approaches yield the highest ROI.',
            'content': 'Artificial intelligence investment has grown exponentially, but returns vary significantly across organizations. This research analyzes data from over 5,000 companies across 22 countries, finding that organizations with comprehensive AI strategies achieve 3-4x higher returns than those pursuing isolated use cases. The paper identifies five critical success factors: data infrastructure quality, cross-functional implementation teams, executive sponsorship, complementary workflow redesign, and ongoing skills development.',
            'published_date': '2024-03-10T00:00:00Z',
            'relevance_score': 0.94
        }
    ]
    
    # Return requested number of articles
    return research_articles[:limit]

# Function to get news articles from NewsAPI
def get_news_api_articles(limit=10):
    """Get articles from NewsAPI with AI focus."""
    if not NEWS_API_KEY:
        log_to_file("No NewsAPI key found. Using sample articles.")
        return []
    
    try:
        # Create a query focused on AI and economics
        query = "(artificial intelligence OR AI OR machine learning OR deep learning OR LLM OR GPT) AND (economy OR business OR industry OR market)"
        
        # Make request to NewsAPI
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&pageSize=30&language=en&sortBy=relevancy"
        response = requests.get(url)
        data = response.json()
        
        if data.get('status') != 'ok':
            log_to_file(f"Error from NewsAPI: {data.get('message', 'Unknown error')}")
            return []
        
        articles = []
        for article in data.get('articles', []):
            # Check if article has AI keywords in title or description
            title = article.get('title', '')
            description = article.get('description', '')
            
            if contains_ai_keywords(title) or contains_ai_keywords(description):
                # Create article object
                article_obj = {
                    'id': hashlib.md5(f"{title}{article.get('url', '')}".encode()).hexdigest(),
                    'title': title,
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'summary': description,
                    'content': article.get('content', ''),
                    'published_date': article.get('publishedAt', datetime.now().isoformat()),
                }
                
                articles.append(article_obj)
        
        log_to_file(f"Found {len(articles)} articles from NewsAPI with AI keywords")
        return articles[:limit]
    
    except Exception as e:
        log_to_file(f"Error fetching from NewsAPI: {str(e)}")
        return []

# Function to summarize text using OpenAI
def summarize_with_openai(text, title=None, max_tokens=150):
    """Summarize text using OpenAI API."""
    if not text:
        return "No content available to summarize."
    
    # Get OpenAI API key from environment variable
    if not OPENAI_API_KEY:
        # If no API key, return a truncated version of the text
        return text[:300] + "..." if len(text) > 300 else text
    
    try:
        # Initialize client
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Create prompt for summarization
        content_text = text[:4000]  # Limit to first 4000 chars for token efficiency
        
        # Call OpenAI API for the summary
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using 3.5 for efficiency and cost
            messages=[
                {"role": "system", "content": "You are a professional AI and economics analyst providing concise, informative summaries."},
                {"role": "user", "content": f"Please provide a concise, informative summary of the following article about AI and economics. Focus on the key points, implications, and any economic analysis.\n\nTitle: {title or 'Article'}\n\nContent:\n{content_text}\n\nSummary (approximately 2-3 sentences):"}
            ],
            max_tokens=max_tokens,
            temperature=0.5  # Lower temperature for more consistent summaries
        )
        
        # Extract summary from response
        summary = response.choices[0].message.content.strip()
        
        # Log the summarization
        log_to_file(f"Generated summary for article: {title or 'Untitled'}")
        
        return summary
        
    except Exception as e:
        log_to_file(f"Error generating summary with OpenAI: {str(e)}")
        # Return a truncated version of the text as fallback
        return text[:300] + "..." if len(text) > 300 else text

# Function to process articles with AI summaries
def process_articles_with_ai_summaries(articles):
    """Process articles to add AI-generated summaries."""
    for article in articles:
        # Get the content to summarize (prefer full content, fall back to existing summary)
        content_to_summarize = article.get('content', article.get('summary', ''))
        
        # Skip if we already have an AI-generated summary
        if article.get('ai_summary'):
            continue
            
        # Generate summary with OpenAI
        if content_to_summarize:
            ai_summary = summarize_with_openai(
                content_to_summarize, 
                title=article.get('title', ''),
                max_tokens=150
            )
            article['ai_summary'] = ai_summary
    
    return articles

# Function to fetch real articles from multiple sources
def fetch_real_articles(limit=10):
    """Fetch articles from multiple sources."""
    # Get articles from different sources
    news_api_articles = get_news_api_articles(limit=20)
    research_articles = get_research_articles(limit=10)
    
    # Combine all articles
    all_articles = news_api_articles + research_articles
    
    # Filter articles for AI relevance
    ai_articles = []
    for article in all_articles:
        # Calculate AI relevance score
        ai_relevance = calculate_ai_relevance_score(article)
        
        # Only include articles with sufficient AI relevance
        if ai_relevance > 0.3:  # Minimum threshold for AI relevance
            article['relevance_score'] = ai_relevance
            ai_articles.append(article)
    
    # Sort by AI relevance score
    ai_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    # Generate AI summaries
    ai_articles = process_articles_with_ai_summaries(ai_articles)
    
    return ai_articles[:limit]

# Routes
@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

@app.route('/api/articles')
def get_articles():
    """Get articles from cache or fetch new ones."""
    refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    # Check if we should refresh the cache
    if refresh or 'articles' not in cache or 'last_updated' not in cache or time.time() - cache['last_updated'] > CACHE_EXPIRY:
        articles = fetch_real_articles()
        
        # Generate AI summaries for the articles
        articles = process_articles_with_ai_summaries(articles)
        
        cache['articles'] = articles
        cache['last_updated'] = time.time()
    
    # Filter articles for AI relevance and sort by score
    ai_articles = []
    for article in cache['articles']:
        # Calculate AI relevance score
        ai_relevance = calculate_ai_relevance_score(article)
        
        # Only include articles with sufficient AI relevance
        if ai_relevance > 0.3:  # Minimum threshold for AI relevance
            article['relevance_score'] = ai_relevance
            ai_articles.append(article)
    
    # Sort by AI relevance score
    ai_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    # Return only the top articles
    return jsonify({
        'articles': ai_articles[:10],  # Return top 10 most relevant articles
        'last_updated': datetime.fromtimestamp(cache['last_updated']).isoformat()
    })

@app.route('/api/refresh')
def refresh_articles():
    """Force refresh of articles."""
    global cache
    
    # Clear cache
    cache = {}
    
    # Fetch new articles
    limit = int(request.args.get('limit', 5))
    articles = fetch_real_articles(limit=limit)
    
    # Ensure all articles have valid URLs
    for article in articles:
        if not article.get('url') or article['url'] == '#' or article['url'] == '':
            # Create a Google search URL as fallback
            article['url'] = f"https://www.google.com/search?q={quote(article['title'] + ' ' + article['source'])}"
    
    # Update cache
    cache['articles'] = articles
    cache['last_updated'] = time.time()
    
    return jsonify({'articles': articles, 'refreshed': True})

@app.route('/api/summarize')
def summarize_articles():
    """Generate AI summaries for all cached articles."""
    if 'articles' not in cache or not cache['articles']:
        # If no articles in cache, fetch them first
        articles = fetch_real_articles()
        cache['articles'] = articles
        cache['last_updated'] = time.time()
    
    # Process all articles with AI summaries
    process_articles_with_ai_summaries(cache['articles'])
    
    # Filter articles for AI relevance and sort by score
    ai_articles = []
    for article in cache['articles']:
        # Calculate AI relevance score
        ai_relevance = calculate_ai_relevance_score(article)
        
        # Only include articles with sufficient AI relevance
        if ai_relevance > 0.3:  # Minimum threshold for AI relevance
            article['relevance_score'] = ai_relevance
            ai_articles.append(article)
    
    # Sort by AI relevance score
    ai_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    # Return only the top articles
    return jsonify({
        'articles': ai_articles[:10],  # Return top 10 most relevant articles
        'last_updated': datetime.fromtimestamp(cache['last_updated']).isoformat()
    })

if __name__ == '__main__':
    # Configure server
    port = int(os.environ.get('PORT', 8000))
    
    # Log server info
    logger.info("=== AI Economic News Agent Production Server ===")
    logger.info(f"Starting server on port {port}")
    logger.info(f"Server will be available at http://localhost:{port}")
    logger.info("Press Ctrl+C to stop the server")
    
    # Run the server
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
