"""
Export utilities for the AI Economic Research News Agent.

This module provides functionality for exporting findings in various formats.
"""

import os
import json
import datetime
from typing import List, Dict, Any
from loguru import logger

from src.models.article import Article
from config.settings import EXPORT_DIRECTORY


def export_findings(
    articles: List[Article],
    format: str = "markdown",
    filename: str = None
) -> str:
    """
    Export the findings to a file in the specified format.
    
    Args:
        articles: List of processed articles
        format: Output format (markdown, json)
        filename: Optional filename (without extension)
        
    Returns:
        Path to the exported file
    """
    # Create export directory if it doesn't exist
    os.makedirs(EXPORT_DIRECTORY, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"ai_economic_research_{today}"
    
    # Export based on format
    if format.lower() == "markdown":
        return export_markdown(articles, filename)
    elif format.lower() == "json":
        return export_json(articles, filename)
    else:
        logger.warning(f"Unsupported export format: {format}. Defaulting to markdown.")
        return export_markdown(articles, filename)


def export_markdown(articles: List[Article], filename: str) -> str:
    """
    Export the findings to a markdown file.
    
    Args:
        articles: List of processed articles
        filename: Filename (without extension)
        
    Returns:
        Path to the exported file
    """
    filepath = os.path.join(EXPORT_DIRECTORY, f"{filename}.md")
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# AI Economic Research Findings\n\n")
            f.write(f"*Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
            
            # Write summary
            f.write(f"## Summary\n\n")
            f.write(f"Found {len(articles)} relevant articles about AI economic research.\n\n")
            
            # Write articles
            f.write(f"## Articles\n\n")
            
            for i, article in enumerate(articles, 1):
                f.write(f"### {i}. {article.content.title}\n\n")
                f.write(f"**Source:** [{article.source.name}]({article.url})\n\n")
                
                if article.metadata.published_date:
                    f.write(f"**Published:** {article.metadata.published_date.strftime('%Y-%m-%d')}\n\n")
                
                if article.analysis and article.analysis.relevance_score:
                    f.write(f"**Relevance Score:** {article.analysis.relevance_score:.2f}\n\n")
                
                if article.analysis and article.analysis.summary:
                    f.write(f"**Summary:**\n\n{article.analysis.summary}\n\n")
                
                if article.analysis and article.analysis.key_findings:
                    f.write(f"**Key Findings:**\n\n")
                    for finding in article.analysis.key_findings:
                        f.write(f"- {finding}\n")
                    f.write("\n")
                
                if article.analysis and article.analysis.economic_indicators:
                    f.write(f"**Economic Indicators:**\n\n")
                    for indicator in article.analysis.economic_indicators:
                        f.write(f"- **{indicator.get('name', 'Indicator')}:** {indicator.get('value', '')}")
                        if 'description' in indicator:
                            f.write(f" - {indicator['description']}")
                        f.write("\n")
                    f.write("\n")
                
                if article.analysis and article.analysis.ai_adoption_metrics:
                    f.write(f"**AI Adoption Metrics:**\n\n")
                    for metric in article.analysis.ai_adoption_metrics:
                        f.write(f"- **{metric.get('name', 'Metric')}:** {metric.get('value', '')}")
                        if 'description' in metric:
                            f.write(f" - {metric['description']}")
                        f.write("\n")
                    f.write("\n")
                
                if article.analysis and article.analysis.keyword_matches:
                    f.write(f"**Keyword Matches:**\n\n")
                    for keyword, count in article.analysis.keyword_matches.items():
                        f.write(f"- {keyword}: {count}\n")
                    f.write("\n")
                
                # Add separator between articles
                if i < len(articles):
                    f.write("---\n\n")
        
        logger.info(f"Exported findings to markdown file: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error exporting to markdown: {str(e)}")
        return ""


def export_json(articles: List[Article], filename: str) -> str:
    """
    Export the findings to a JSON file.
    
    Args:
        articles: List of processed articles
        filename: Filename (without extension)
        
    Returns:
        Path to the exported file
    """
    filepath = os.path.join(EXPORT_DIRECTORY, f"{filename}.json")
    
    try:
        # Convert articles to JSON-serializable format
        articles_data = []
        for article in articles:
            article_dict = article.dict()
            
            # Convert datetime objects to strings
            if article.metadata.published_date:
                article_dict["metadata"]["published_date"] = article.metadata.published_date.isoformat()
            if article.metadata.modified_date:
                article_dict["metadata"]["modified_date"] = article.metadata.modified_date.isoformat()
            
            articles_data.append(article_dict)
        
        # Create output data structure
        output_data = {
            "generated_at": datetime.datetime.now().isoformat(),
            "article_count": len(articles),
            "articles": articles_data
        }
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Exported findings to JSON file: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error exporting to JSON: {str(e)}")
        return ""
