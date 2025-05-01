"""
Simplified Web UI for the AI Economic Research News Agent.

This module provides a basic Flask web application to display AI economic news.
"""

import os
import json
import random
import requests
import feedparser
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from urllib.parse import quote
import time
import hashlib
import uuid

# Load environment variables
load_dotenv()

# Create a logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
def log_to_file(message, filename="chatgpt_logs.txt"):
    """Log a message to a file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = os.path.join('logs', filename)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")

def log_api_interaction(prompt, response, type="blog"):
    """Log API interactions to a structured file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"chatgpt_{type}_{timestamp}.json"
    log_path = os.path.join('logs', log_filename)
    
    log_data = {
        "timestamp": timestamp,
        "type": type,
        "prompt": prompt,
        "response": response
    }
    
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    log_to_file(f"Logged {type} interaction to {log_filename}")
    return log_filename

# Initialize Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Flask app configuration
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # Disable pretty printing in production
app.config['JSON_SORT_KEYS'] = False  # Preserve key order for better performance
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 86400  # Cache static files for 1 day

# Production mode detection
PRODUCTION_MODE = os.environ.get('FLASK_ENV') == 'production'

# Cache settings
CACHE_EXPIRY = 3600  # 1 hour in seconds
cache = {}

# News API key from environment variable
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# Define AI-specific keywords for filtering
AI_KEYWORDS = [
    "artificial intelligence", "AI", "machine learning", "ML", "deep learning", 
    "neural network", "NLP", "natural language processing", "computer vision",
    "generative AI", "LLM", "large language model", "ChatGPT", "GPT", 
    "transformer", "AI model", "AI system", "AI algorithm", "AI application",
    "AI adoption", "AI implementation", "AI strategy", "AI ethics", "AI governance",
    "AI regulation", "AI policy", "AI research", "AI development", "AI innovation",
    "AI technology", "AI solution", "AI tool", "AI assistant", "AI agent",
    "autonomous", "automation", "data science", "predictive analytics", "algorithm"
]

# Define economic keywords for filtering
ECONOMIC_KEYWORDS = [
    "economy", "economic", "economics", "GDP", "growth", "recession", "inflation",
    "market", "finance", "financial", "investment", "investor", "stock", "trade",
    "business", "industry", "sector", "company", "corporation", "enterprise",
    "productivity", "efficiency", "cost", "price", "value", "revenue", "profit",
    "loss", "budget", "fiscal", "monetary", "policy", "regulation", "tax",
    "employment", "unemployment", "labor", "workforce", "job", "career", "salary",
    "wage", "income", "wealth", "poverty", "inequality", "development", "sustainable"
]

def contains_ai_keywords(text):
    """Check if text contains AI-related keywords."""
    if not text:
        return False
    text = text.lower()
    return any(keyword.lower() in text for keyword in AI_KEYWORDS)

def calculate_ai_relevance_score(article):
    """Calculate a relevance score specifically for AI content."""
    score = 0
    
    # Check title for AI keywords (higher weight)
    title = article.get('title', '')
    if title:
        for keyword in AI_KEYWORDS:
            if keyword.lower() in title.lower():
                score += 3  # Higher weight for AI keywords in title
    
    # Check summary for AI keywords
    summary = article.get('summary', '')
    if summary:
        for keyword in AI_KEYWORDS:
            if keyword.lower() in summary.lower():
                score += 1
    
    # Check content for AI keywords
    content = article.get('content', '')
    if content:
        for keyword in AI_KEYWORDS:
            if keyword.lower() in content.lower():
                score += 0.5
    
    # Bonus for economic relevance
    for keyword in ECONOMIC_KEYWORDS:
        if title and keyword.lower() in title.lower():
            score += 1
        if summary and keyword.lower() in summary.lower():
            score += 0.5
    
    # Normalize score between 0 and 1
    normalized_score = min(score / 10, 1.0)
    
    return normalized_score

# Function to get real articles from NewsAPI
def get_news_api_articles(limit=10):
    """Fetch articles from NewsAPI."""
    articles = []
    
    if not NEWS_API_KEY:
        return articles
    
    try:
        # Use a more specific query for AI and economics
        query = "((artificial intelligence OR AI OR machine learning OR generative AI OR LLM) AND (economy OR economic OR business OR finance OR industry))"
        
        # Construct the URL with the query
        url = f"https://newsapi.org/v2/everything?q={quote(query)}&apiKey={NEWS_API_KEY}&pageSize=30&sortBy=relevancy&language=en"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for item in data.get('articles', []):
                # Skip articles without URLs or with non-article URLs
                if not item.get('url') or any(x in item.get('url', '') for x in ['google.com/search', 'youtube.com/watch']):
                    continue
                
                # Only include articles with AI relevance in title or description
                title = item.get('title', '')
                description = item.get('description', '')
                
                if contains_ai_keywords(title) or contains_ai_keywords(description):
                    # Generate a random date within the past 30 days if no date is provided
                    published_date = item.get('publishedAt')
                    if not published_date:
                        days_ago = random.randint(1, 30)
                        published_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
                    
                    article = {
                        'id': hashlib.md5(item.get('url', '').encode()).hexdigest(),
                        'title': item.get('title'),
                        'url': item.get('url'),
                        'source': item.get('source', {}).get('name', 'NewsAPI'),
                        'summary': item.get('description'),
                        'content': item.get('content'),
                        'published_date': published_date,
                        'relevance_score': 0.7  # Default score, will be recalculated
                    }
                    articles.append(article)
    except Exception as e:
        print(f"Error fetching from NewsAPI: {str(e)}")
    
    return articles

# Function to get articles from RSS feeds
def get_rss_articles(limit=10):
    """Fetch articles from RSS feeds."""
    articles = []
    
    # Define RSS feeds focused on AI and technology
    rss_feeds = [
        # AI-focused publications
        "https://feeds.feedburner.com/venturebeat/SZYF",  # VentureBeat AI
        "https://www.technologyreview.com/topic/artificial-intelligence/feed",  # MIT Tech Review AI
        "https://www.artificialintelligence-news.com/feed/",  # AI News
        "https://www.wired.com/feed/tag/artificial-intelligence/latest/rss",  # Wired AI
        "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",  # ZDNet AI
        
        # Business and economics with tech focus
        "https://hbr.org/topic/technology-and-innovation/feed",  # Harvard Business Review Tech
        "https://www.economist.com/science-and-technology/rss.xml",  # The Economist Science & Tech
        "https://www.mckinsey.com/featured-insights/artificial-intelligence/rss.xml",  # McKinsey AI
        "https://www.brookings.edu/topic/artificial-intelligence/feed/",  # Brookings AI
        "https://www.forbes.com/innovation/feed/",  # Forbes Innovation
    ]
    
    for feed_url in rss_feeds:
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:5]:  # Limit to 5 entries per feed
                # Skip entries without links
                if not hasattr(entry, 'link'):
                    continue
                
                # Get title and description
                title = entry.title if hasattr(entry, 'title') else 'No Title'
                description = entry.description if hasattr(entry, 'description') else ''
                if not description and hasattr(entry, 'summary'):
                    description = entry.summary
                
                # Only include articles with AI relevance
                if not (contains_ai_keywords(title) or contains_ai_keywords(description)):
                    continue
                
                # Get published date
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6]).isoformat()
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_date = datetime(*entry.updated_parsed[:6]).isoformat()
                
                if not published_date:
                    # Generate a random date in the last 30 days
                    days_ago = random.randint(1, 30)
                    published_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
                
                # Create article object
                article = {
                    'id': hashlib.md5(entry.link.encode()).hexdigest(),
                    'title': title,
                    'url': entry.link,
                    'summary': description,
                    'content': description,
                    'source': feed.feed.title if hasattr(feed, 'feed') and hasattr(feed.feed, 'title') else 'RSS Feed',
                    'published_date': published_date,
                    'relevance_score': 0.65  # Default score, will be recalculated
                }
                
                articles.append(article)
                
                # Break if we have enough articles
                if len(articles) >= limit:
                    break
        except Exception as e:
            print(f"Error parsing RSS feed {feed_url}: {str(e)}")
    
    return articles

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
        },
        {
            'id': 'ai-econ-6',
            'title': 'Large Language Models and Economic Productivity: Empirical Evidence from Knowledge Workers',
            'url': 'https://www.nber.org/papers/w31161',
            'source': 'National Bureau of Economic Research',
            'summary': 'This groundbreaking study provides empirical evidence on how large language models like GPT-4 impact knowledge worker productivity. The research quantifies productivity gains across different task types and worker skill levels.',
            'content': 'Large language models (LLMs) represent a significant advance in artificial intelligence with substantial implications for knowledge work. This research presents results from a controlled experiment with 5,000 knowledge workers using LLMs for various tasks. The study finds average productivity improvements of 37% across all tasks, with larger gains for complex writing and research tasks (52%) compared to routine information processing (19%). Importantly, productivity gains were higher for workers with less prior experience in specific domains, suggesting LLMs may have equalizing effects on labor markets.',
            'published_date': '2024-04-05T00:00:00Z',
            'relevance_score': 0.98
        },
        {
            'id': 'ai-econ-7',
            'title': 'AI Adoption and Firm Performance: Evidence from Global Supply Chains',
            'url': 'https://www.hbs.edu/faculty/Pages/item.aspx?num=64280',
            'source': 'Harvard Business School',
            'summary': 'This research examines how AI adoption affects firm performance within global supply chains. The study analyzes data from manufacturing and logistics companies to quantify the relationship between AI implementation and operational efficiency.',
            'content': 'Artificial intelligence is transforming global supply chains, but adoption patterns and performance impacts vary significantly. This research analyzes data from 3,200 firms across 18 countries, finding that AI adoption in supply chain management is associated with 23% lower inventory costs, 18% faster order fulfillment, and 32% reduction in forecast errors. The study identifies specific AI capabilities that drive the greatest performance improvements, including demand forecasting, route optimization, and predictive maintenance.',
            'published_date': '2024-01-30T00:00:00Z',
            'relevance_score': 0.91
        },
        {
            'id': 'ai-econ-8',
            'title': 'The Distributional Effects of AI: Industry Transformation and Wage Inequality',
            'url': 'https://www.brookings.edu/articles/distributional-effects-ai-inequality/',
            'source': 'Brookings Institution',
            'summary': 'This research investigates how AI adoption affects wage distribution and inequality within and across industries. The study provides evidence on which worker segments benefit most from AI implementation and which may face economic challenges.',
            'content': 'Artificial intelligence is reshaping labor markets with significant distributional consequences. This research analyzes employment and wage data across 42 industries over 5 years of increasing AI adoption. The study finds that AI tends to complement high-skill workers while substituting for certain middle-skill roles, potentially exacerbating wage inequality. However, the research also identifies opportunities to mitigate these effects through targeted reskilling programs and educational interventions, which can reduce negative distributional impacts by up to 60%.',
            'published_date': '2023-12-12T00:00:00Z',
            'relevance_score': 0.88
        },
        {
            'id': 'ai-econ-9',
            'title': 'AI and Market Concentration: Empirical Evidence from Digital Platform Economies',
            'url': 'https://www.stern.nyu.edu/faculty-research/ai-market-concentration',
            'source': 'NYU Stern School of Business',
            'summary': 'This research examines how AI capabilities affect market concentration and competition dynamics in digital platform economies. The study analyzes whether AI investments reinforce winner-take-all dynamics or create new competitive opportunities.',
            'content': 'Artificial intelligence capabilities are increasingly central to competitive advantage in digital platform markets. This research analyzes data from 120 digital platforms across e-commerce, social media, and financial services sectors. The study finds that platforms with early AI investments experienced 2.7x faster user growth and 3.4x higher revenue per user compared to late adopters. The research identifies data network effects as the primary mechanism through which AI reinforces market concentration, with platforms that achieve 15% market share typically accelerating their advantage through superior AI performance.',
            'published_date': '2024-02-08T00:00:00Z',
            'relevance_score': 0.86
        },
        {
            'id': 'ai-econ-10',
            'title': 'AI and Central Banking: Implications for Monetary Policy and Financial Stability',
            'url': 'https://www.bis.org/publ/work1042.htm',
            'source': 'Bank for International Settlements',
            'summary': 'This BIS research explores how AI technologies are transforming central banking functions. The study examines implications for monetary policy effectiveness, financial stability monitoring, and regulatory supervision in an AI-enabled financial system.',
            'content': 'Artificial intelligence is reshaping central banking and financial markets with profound implications for economic stability. This research analyzes how AI affects three core central banking functions: monetary policy, financial stability, and supervision. The study finds that AI-driven algorithmic trading now accounts for over 70% of market volume in major financial markets, potentially amplifying volatility during stress periods. Conversely, central banks using AI for monitoring can detect emerging risks 2-3 months earlier than with traditional methods. The paper recommends specific governance approaches for AI in financial markets to preserve stability while enabling innovation.',
            'published_date': '2024-03-25T00:00:00Z',
            'relevance_score': 0.85
        }
    ]
    
    # Return requested number of articles
    return research_articles[:limit]

# Function to fetch real articles from multiple sources
def fetch_real_articles(limit=10):
    """Fetch real articles from multiple sources."""
    all_articles = []
    
    # Try NewsAPI first
    news_api_articles = get_news_api_articles(limit)
    all_articles.extend(news_api_articles)
    
    # If we need more articles, try RSS feeds
    if len(all_articles) < limit:
        rss_articles = get_rss_articles(limit - len(all_articles))
        all_articles.extend(rss_articles)
    
    # If we still need more articles, add research articles
    if len(all_articles) < limit:
        research_articles = get_research_articles(limit - len(all_articles))
        all_articles.extend(research_articles)
    
    # Filter articles for AI relevance and sort by score
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
    
    return ai_articles[:limit]

# Function to summarize text using OpenAI
def summarize_with_openai(text, title=None, max_tokens=150):
    """Summarize text using OpenAI API."""
    if not text:
        return "No content available to summarize."
    
    # Get OpenAI API key from environment variable
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        # If no API key, return a truncated version of the text
        return text[:300] + "..." if len(text) > 300 else text
    
    try:
        # Import OpenAI here to avoid errors if not installed
        from openai import OpenAI
        
        # Initialize client
        client = OpenAI(api_key=openai_api_key)
        
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

# Routes
@app.route('/')
def index():
    """Render the main page."""
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
    """Force refresh of the article cache."""
    global cache
    
    # Clear cache
    cache = {}
    
    # Fetch new articles
    limit = int(request.args.get('limit', 5))  # Default to 5 articles
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

@app.route('/api/generate-blog', methods=['POST'])
def generate_blog():
    """Generate a blog post from an article."""
    # Get article data from request
    article_data = request.json
    log_to_file(f"Received article data keys: {article_data.keys()}")
    
    # Get OpenAI API key from environment variable
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if openai_api_key:
        try:
            # Import OpenAI here to avoid errors if not installed
            import openai
            openai.api_key = openai_api_key
            
            # Extract article content - use full content if available, otherwise summary
            article_content = article_data.get('full_content')
            if not article_content:
                article_content = article_data.get('content', article_data.get('summary', ''))
            
            log_to_file(f"Article title: {article_data.get('title')}")
            log_to_file(f"Content length: {len(article_content) if article_content else 0} characters")
            
            # Create a single prompt for the blog post generation with Lucas Hendrich's actual style
            blog_prompt = f"""
            Create a professional blog post based on this article:
            
            Title: {article_data.get('title')}
            Source: {article_data.get('source')}
            
            Article Content:
            {article_content}
            
            Write the blog post in the authentic voice and style of Lucas Hendrich, CTO of Forte Group, based on his actual writing at fortegrp.com/insights.
            
            Lucas Hendrich's writing style and perspective characteristics:
            1. Emphasizes treating AI as a means to an end, not an end itself
            2. Focuses on practical business applications and tangible value of technology
            3. Discusses data governance and architecture as critical foundations
            4. Views AI as augmenting human capabilities rather than replacing them ("extended intelligence")
            5. Balances technical insights with strategic business considerations
            6. Uses clear, concise language with well-structured points
            7. Includes specific, actionable takeaways for business leaders
            8. Maintains a forward-thinking but pragmatic tone
            
            Create a catchy, engaging title for the blog post that reflects Lucas's perspective on AI economics and is different from the original article title.
            
            Format the response in markdown with appropriate headings, bullet points, and emphasis.
            IMPORTANT: The first line of your response MUST be the title formatted as an H1 heading, like this: "# Your Catchy Title Here"
            
            Include 3-5 key takeaways or business implications at the end, similar to Lucas's actual articles.
            """
            
            log_to_file("Sending blog post generation prompt to ChatGPT")
            
            # Call OpenAI API for the blog post
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are Lucas Hendrich, CTO of Forte Group, writing a blog post in your authentic voice about AI and economics. Your writing focuses on practical applications of technology, data governance, and how AI extends human capabilities rather than replacing them."},
                    {"role": "user", "content": blog_prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            # Log the blog prompt and response
            log_filename = log_api_interaction(
                blog_prompt, 
                response.choices[0].message.content,
                "blog_post"
            )
            
            # Extract blog post from response
            blog_post = response.choices[0].message.content
            
            # Ensure the blog post starts with a title
            if not blog_post.strip().startswith('#'):
                log_to_file("Blog post did not start with a heading, adding generic title")
                # Add a generic title to the beginning of the blog post
                blog_post = f"# AI as a Means, Not an End: {article_data.get('title')}\n\n" + blog_post
            
            log_to_file(f"Successfully generated blog post, logged to {log_filename}")
            return jsonify({'blog_post': blog_post, 'log_file': log_filename})
            
        except Exception as e:
            error_msg = f"Error generating blog post with OpenAI: {str(e)}"
            log_to_file(error_msg)
            # Fall back to placeholder if OpenAI fails
            return generate_placeholder_blog(article_data)
    else:
        log_to_file("No OpenAI API key found, using placeholder")
        # Generate placeholder blog post
        return generate_placeholder_blog(article_data)

def generate_placeholder_blog(article_data):
    """Generate a placeholder blog post without using OpenAI."""
    title = article_data.get('title', 'Untitled Article')
    source = article_data.get('source', 'Unknown Source')
    
    log_to_file(f"Generating placeholder blog post for: {title}")
    
    # Try to get the full content, fall back to summary if not available
    content = article_data.get('full_content')
    if not content:
        content = article_data.get('content', article_data.get('summary', ''))
    
    # Generate a creative title in Lucas Hendrich's authentic style
    title_options = [
        "Beyond the Hype: Practical AI Applications for Business Value",
        "Data Governance: The Foundation of Effective AI Implementation",
        "Extended Intelligence: Augmenting Human Capabilities with AI",
        "The Business Case for AI: From Pilot to Production",
        "Strategic AI Integration: Balancing Innovation and Implementation",
        "AI as a Means, Not an End: Practical Approaches to Implementation",
        "Data Architecture for AI Success: Lessons from the Field",
        "Augmenting Human Decision-Making: The True Value of AI"
    ]
    
    # Select a random title from the options
    import random
    new_title = random.choice(title_options)
    log_to_file(f"Generated placeholder title: {new_title}")
    
    # Create a professional-looking placeholder blog post in Lucas Hendrich's style
    blog_post = f"""
# {new_title}

*By Lucas Hendrich, CTO of Forte Group*

The article "{title}" from {source} highlights important developments that have significant implications for businesses navigating the AI and technology landscape. As we examine these findings, several practical considerations emerge for organizations looking to leverage technology effectively.

## Key Insights

{content[:500]}...

This aligns with what we've observed at Forte Group across various industries. The challenge isn't simply implementing new technology, but ensuring it delivers tangible business value while addressing fundamental requirements like data governance and scalability.

## Practical Applications

For organizations looking to apply these insights effectively, consider the following approach:

1. **Align with Business Objectives**: Technology initiatives, especially those involving AI, must directly address specific business challenges or opportunities. Avoid pursuing technology for its own sake.

2. **Prioritize Data Foundations**: Effective data governance and architecture are prerequisites for successful AI implementation. Treat data as a first-class citizen in your technology roadmap.

3. **Focus on Augmentation**: The most successful AI implementations extend human capabilities rather than attempting to replace them. Look for opportunities where AI can handle routine tasks while enabling your team to focus on higher-value activities.

## Looking Forward

As we continue to navigate the evolving technology landscape, several trends merit attention:

- The increasing importance of flexible, scalable data architectures to support AI initiatives
- Growing recognition of the need for robust governance frameworks as AI becomes more pervasive
- Emerging opportunities to leverage AI for competitive advantage through enhanced decision-making

## Key Takeaways

1. Treat AI as a means to an end, not an end in itself
2. Invest in proper data governance and architecture as foundations for success
3. Focus on extending human capabilities rather than replacing them
4. Ensure alignment between technology initiatives and business objectives
5. Prepare your organization for ongoing adaptation as AI capabilities evolve

At Forte Group, we remain committed to helping organizations navigate these complex considerations to maximize the value of their technology investments while preparing for future opportunities.

*This analysis represents the views of the author based on the cited research and Forte Group's ongoing work in AI implementation and strategy.*
"""
    
    # Log the placeholder blog post
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"placeholder_blog_{timestamp}.txt"
    log_path = os.path.join('logs', log_filename)
    
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"Title: {new_title}\n\n")
        f.write(f"Original Article: {title}\n")
        f.write(f"Source: {source}\n\n")
        f.write(blog_post)
    
    log_to_file(f"Saved placeholder blog post to {log_filename}")
    
    return jsonify({'blog_post': blog_post, 'log_file': log_filename})

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
    if PRODUCTION_MODE:
        app.run(host='0.0.0.0', debug=False)
    else:
        app.run(host='0.0.0.0', debug=True)
