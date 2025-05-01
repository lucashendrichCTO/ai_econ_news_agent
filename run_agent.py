#!/usr/bin/env python
"""
Run script for the AI Economic Research News Agent.

This script provides a simple way to run the agent with default settings.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import agent components
from src.agents.news_agent import AIEconomicNewsAgent
from src.utils.export import export_findings
from config.settings import ARTICLES_PER_DAY, DEFAULT_OUTPUT_FORMAT

def main():
    """Run the AI Economic News Agent."""
    print("\n=== AI Economic Research News Agent ===\n")
    
    try:
        # Initialize the agent
        print("Initializing agent...")
        agent = AIEconomicNewsAgent()
        
        # Find relevant articles
        print(f"\nSearching for up to {ARTICLES_PER_DAY} relevant articles...")
        articles = agent.find_articles(limit=ARTICLES_PER_DAY)
        
        if not articles:
            print("\nNo relevant articles found.")
            return
        
        print(f"\nFound {len(articles)} relevant articles:")
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article.content.title}")
            print(f"   Source: {article.source.name}")
            print(f"   Relevance: {article.analysis.relevance_score:.2f}")
        
        # Process and analyze the articles
        print("\nProcessing articles...")
        processed_articles = agent.process_articles(articles)
        
        # Export the findings
        today = datetime.now().strftime("%Y-%m-%d")
        export_path = export_findings(
            processed_articles, 
            format=DEFAULT_OUTPUT_FORMAT,
            filename=f"ai_economic_research_{today}"
        )
        
        print(f"\nExported findings to: {export_path}")
        print("\nDone!")
        
    except Exception as e:
        print(f"\nError running agent: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
