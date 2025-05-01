"""
Web UI for the AI Economic Research News Agent.

This module provides a Flask web application to display the latest economic research news about AI adoption.
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import agent components
from src.agents.news_agent import AIEconomicNewsAgent
from src.utils.export import export_findings
from config.settings import ARTICLES_PER_DAY

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)

# Initialize the agent
agent = AIEconomicNewsAgent()


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/articles')
def get_articles():
    """API endpoint to get the latest articles."""
    try:
        # Check if we should use cached results
        use_cache = request.args.get('cache', 'true').lower() == 'true'
        
        if use_cache:
            # Try to load from cache first
            cache_path = os.path.join(os.path.dirname(__file__), 'static/data/latest_articles.json')
            if os.path.exists(cache_path):
                # Check if cache is from today
                cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
                if cache_time.date() == datetime.now().date():
                    with open(cache_path, 'r') as f:
                        return jsonify(json.load(f))
        
        # Get the latest articles
        limit = int(request.args.get('limit', ARTICLES_PER_DAY))
        articles = agent.find_articles(limit=limit)
        
        # Process the articles
        processed_articles = agent.process_articles(articles)
        
        # Convert to JSON-serializable format
        articles_data = []
        for article in processed_articles:
            article_dict = {
                "id": article.id,
                "title": article.content.title,
                "url": str(article.url),
                "source": {
                    "name": article.source.name,
                    "url": str(article.source.url),
                    "quality_score": article.source.quality_score
                },
                "relevance_score": article.analysis.relevance_score if article.analysis else None,
                "summary": article.analysis.summary if article.analysis else None,
                "key_findings": article.analysis.key_findings if article.analysis else [],
                "economic_indicators": article.analysis.economic_indicators if article.analysis else [],
                "ai_adoption_metrics": article.analysis.ai_adoption_metrics if article.analysis else [],
                "word_count": article.content.word_count,
                "published_date": article.metadata.published_date.isoformat() if article.metadata.published_date else None
            }
            articles_data.append(article_dict)
        
        # Save to cache
        os.makedirs(os.path.join(os.path.dirname(__file__), 'static/data'), exist_ok=True)
        with open(os.path.join(os.path.dirname(__file__), 'static/data/latest_articles.json'), 'w') as f:
            json.dump(articles_data, f)
        
        return jsonify(articles_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/refresh')
def refresh_articles():
    """API endpoint to force a refresh of the articles."""
    try:
        # Get the latest articles
        limit = int(request.args.get('limit', ARTICLES_PER_DAY))
        articles = agent.find_articles(limit=limit)
        
        # Process the articles
        processed_articles = agent.process_articles(articles)
        
        # Export the findings
        today = datetime.now().strftime("%Y-%m-%d")
        export_findings(
            processed_articles, 
            format="json",
            filename=f"ai_economic_research_{today}"
        )
        
        # Convert to JSON-serializable format
        articles_data = []
        for article in processed_articles:
            article_dict = {
                "id": article.id,
                "title": article.content.title,
                "url": str(article.url),
                "source": {
                    "name": article.source.name,
                    "url": str(article.source.url),
                    "quality_score": article.source.quality_score
                },
                "relevance_score": article.analysis.relevance_score if article.analysis else None,
                "summary": article.analysis.summary if article.analysis else None,
                "key_findings": article.analysis.key_findings if article.analysis else [],
                "economic_indicators": article.analysis.economic_indicators if article.analysis else [],
                "ai_adoption_metrics": article.analysis.ai_adoption_metrics if article.analysis else [],
                "word_count": article.content.word_count,
                "published_date": article.metadata.published_date.isoformat() if article.metadata.published_date else None
            }
            articles_data.append(article_dict)
        
        # Save to cache
        os.makedirs(os.path.join(os.path.dirname(__file__), 'static/data'), exist_ok=True)
        with open(os.path.join(os.path.dirname(__file__), 'static/data/latest_articles.json'), 'w') as f:
            json.dump(articles_data, f)
        
        return jsonify({"status": "success", "message": "Articles refreshed", "count": len(articles_data)})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(os.path.join(os.path.dirname(__file__), 'static/data'), exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
