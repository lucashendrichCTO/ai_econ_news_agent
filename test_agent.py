"""
Test script for the AI Economic Research News Agent.

This script allows you to test the agent's functionality with different options.
"""

import os
import sys
import argparse
from loguru import logger

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import agent components
from src.agents.news_agent import AIEconomicNewsAgent
from src.utils.export import export_findings
from config.settings import DEFAULT_OUTPUT_FORMAT


def test_find_articles(limit=3):
    """Test the article finding functionality."""
    print(f"\n--- Testing article finding (limit: {limit}) ---")
    
    agent = AIEconomicNewsAgent()
    articles = agent.find_articles(limit=limit)
    
    print(f"Found {len(articles)} articles:")
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article.content.title}")
        print(f"   Source: {article.source.name}")
        print(f"   URL: {article.url}")
        print(f"   Relevance: {article.analysis.relevance_score:.2f}")
    
    return articles


def test_process_articles(articles=None):
    """Test the article processing functionality."""
    print("\n--- Testing article processing ---")
    
    agent = AIEconomicNewsAgent()
    
    if articles is None:
        print("Getting recent articles from storage...")
        articles = agent.get_stored_articles(days=7)
        
        if not articles:
            print("No articles found in storage. Finding new articles...")
            articles = agent.find_articles(limit=2)
    
    print(f"Processing {len(articles)} articles...")
    processed_articles = agent.process_articles(articles)
    
    print(f"Processed {len(processed_articles)} articles:")
    for i, article in enumerate(processed_articles, 1):
        print(f"\n{i}. {article.content.title}")
        
        if article.analysis and article.analysis.summary:
            print(f"\n   Summary: {article.analysis.summary[:150]}...")
        
        if article.analysis and article.analysis.key_findings:
            print("\n   Key Findings:")
            for j, finding in enumerate(article.analysis.key_findings[:2], 1):
                print(f"   {j}. {finding}")
        
        if article.analysis and article.analysis.economic_indicators:
            print("\n   Economic Indicators:")
            for j, indicator in enumerate(article.analysis.economic_indicators[:2], 1):
                print(f"   {j}. {indicator.get('name')}: {indicator.get('value')}")
    
    return processed_articles


def test_export(articles):
    """Test the export functionality."""
    print("\n--- Testing export functionality ---")
    
    if not articles:
        print("No articles to export.")
        return
    
    export_path = export_findings(articles, format=DEFAULT_OUTPUT_FORMAT)
    
    if export_path:
        print(f"Successfully exported to: {export_path}")
    else:
        print("Export failed.")


def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(description="Test the AI Economic News Agent")
    parser.add_argument("--find", action="store_true", help="Test finding articles")
    parser.add_argument("--process", action="store_true", help="Test processing articles")
    parser.add_argument("--export", action="store_true", help="Test exporting findings")
    parser.add_argument("--all", action="store_true", help="Test all functionality")
    parser.add_argument("--limit", type=int, default=3, help="Number of articles to find")
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not (args.find or args.process or args.export or args.all):
        parser.print_help()
        return
    
    articles = None
    
    try:
        if args.find or args.all:
            articles = test_find_articles(args.limit)
        
        if args.process or args.all:
            articles = test_process_articles(articles)
        
        if args.export or args.all:
            test_export(articles)
            
    except Exception as e:
        logger.exception("Error during testing")
        print(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()
