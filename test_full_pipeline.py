#!/usr/bin/env python
"""
Test script for running the full AI Economic News Agent pipeline.

This script tests the complete workflow: finding articles, processing them,
generating summaries, and exporting the results.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

# Import agent components
from src.agents.news_agent import AIEconomicNewsAgent
from src.utils.export import export_findings
from src.utils.notification import send_email_notification
from config.settings import (
    ARTICLES_PER_DAY,
    DEFAULT_OUTPUT_FORMAT,
    ENABLE_EMAIL_NOTIFICATIONS,
    EMAIL_RECIPIENTS,
    EMAIL_SUBJECT_TEMPLATE
)

def test_full_pipeline():
    """Test the full agent pipeline."""
    print("\n=== Testing AI Economic News Agent Full Pipeline ===\n")
    
    try:
        # Initialize the agent
        print("Initializing agent...")
        agent = AIEconomicNewsAgent()
        
        # Find relevant articles
        print(f"\nSearching for up to {ARTICLES_PER_DAY} relevant articles...")
        articles = agent.find_articles(limit=ARTICLES_PER_DAY)
        
        if not articles:
            print("\nNo relevant articles found.")
            return False
        
        print(f"\nFound {len(articles)} relevant articles:")
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article.content.title}")
            print(f"   Source: {article.source.name}")
            print(f"   URL: {article.url}")
            print(f"   Relevance: {article.analysis.relevance_score:.2f}")
        
        # Process and analyze the articles
        print("\nProcessing articles...")
        processed_articles = agent.process_articles(articles)
        
        print("\nProcessed articles:")
        for i, article in enumerate(processed_articles, 1):
            print(f"\n{i}. {article.content.title}")
            
            if article.analysis and article.analysis.summary:
                summary = article.analysis.summary[:100] + "..." if len(article.analysis.summary) > 100 else article.analysis.summary
                print(f"   Summary: {summary}")
            
            if article.analysis and article.analysis.key_findings:
                print(f"   Key Findings: {len(article.analysis.key_findings)} found")
            
            if article.analysis and article.analysis.economic_indicators:
                print(f"   Economic Indicators: {len(article.analysis.economic_indicators)} found")
            
            if article.analysis and article.analysis.ai_adoption_metrics:
                print(f"   AI Adoption Metrics: {len(article.analysis.ai_adoption_metrics)} found")
        
        # Export the findings
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Export as markdown
        markdown_path = export_findings(
            processed_articles, 
            format="markdown",
            filename=f"ai_economic_research_{today}"
        )
        print(f"\nExported findings to markdown: {markdown_path}")
        
        # Export as JSON
        json_path = export_findings(
            processed_articles, 
            format="json",
            filename=f"ai_economic_research_{today}"
        )
        print(f"Exported findings to JSON: {json_path}")
        
        # Send email notification if enabled
        if ENABLE_EMAIL_NOTIFICATIONS and EMAIL_RECIPIENTS:
            print("\nSending email notification...")
            email_subject = EMAIL_SUBJECT_TEMPLATE.format(date=today)
            success = send_email_notification(
                recipients=EMAIL_RECIPIENTS,
                subject=email_subject,
                articles=processed_articles,
                export_path=markdown_path
            )
            
            if success:
                print(f"Email notification sent to: {', '.join(EMAIL_RECIPIENTS)}")
            else:
                print("Failed to send email notification. Check SMTP settings.")
        
        print("\nFull pipeline test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nError during pipeline test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_full_pipeline()
    sys.exit(0 if success else 1)
