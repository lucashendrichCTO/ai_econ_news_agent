"""
AI Economic News Agent implementation.

This module implements the main agent that finds economic research news about AI adoption.
"""

import json
import os
from typing import List, Dict, Any
from loguru import logger

from src.models.article import Article, ArticleSource, ArticleContent, ArticleMetadata, ArticleAnalysis
from src.services.web_scraper import WebScraper
from src.services.content_analyzer import ContentAnalyzer
from src.services.article_storage import ArticleStorage
from src.utils.relevance import calculate_relevance_score
from config.settings import (
    PRIMARY_KEYWORDS,
    SECONDARY_KEYWORDS,
    REQUIRED_TERMS,
    EXCLUDED_TERMS,
    MIN_ARTICLE_LENGTH,
    MAX_ARTICLE_AGE
)


class AIEconomicNewsAgent:
    """
    Agent that finds and processes economic research news about AI adoption.
    
    This class implements the Model Concept Protocol (MCP) design pattern:
    - Models: Article and related data structures
    - Concepts: Finding, analyzing, and processing articles
    - Protocols: Interfaces for external service interactions
    """
    
    def __init__(self):
        """Initialize the AI Economic News Agent."""
        # Load news sources from configuration
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'sources.json')
        with open(config_path, 'r') as f:
            self.sources_config = json.load(f)
        
        # Initialize services
        self.scraper = WebScraper()
        self.analyzer = ContentAnalyzer()
        self.storage = ArticleStorage()
        
        logger.info(f"Initialized AI Economic News Agent with {len(self.sources_config['news_sources'])} news sources")
    
    def find_articles(self, limit: int = 5) -> List[Article]:
        """
        Find relevant articles about economic research on AI adoption.
        
        Args:
            limit: Maximum number of articles to return
            
        Returns:
            List of relevant articles
        """
        all_articles = []
        
        # Search each news source
        for source_config in self.sources_config['news_sources']:
            try:
                logger.info(f"Searching {source_config['name']}")
                
                # Create source object
                source = ArticleSource(
                    name=source_config['name'],
                    url=source_config['url'],
                    quality_score=source_config['quality_score'],
                    type=source_config['type']
                )
                
                # Fetch and process articles from this source
                raw_articles = self.scraper.fetch_articles_from_source(
                    source_config,
                    keywords=PRIMARY_KEYWORDS
                )
                
                # Convert raw articles to Article objects
                for raw in raw_articles:
                    try:
                        # Extract content
                        content_data = self.scraper.extract_content(raw['url'], source_config)
                        
                        # Skip if content is too short
                        if len(content_data['text'].split()) < MIN_ARTICLE_LENGTH:
                            logger.debug(f"Skipping article (too short): {raw['title']}")
                            continue
                        
                        # Create article object
                        article = Article(
                            url=raw['url'],
                            source=source,
                            content=ArticleContent(
                                title=raw['title'],
                                text=content_data['text'],
                                html=content_data.get('html')
                            ),
                            metadata=ArticleMetadata(
                                authors=content_data.get('authors', []),
                                published_date=content_data.get('published_date'),
                                categories=content_data.get('categories', []),
                                tags=content_data.get('tags', [])
                            )
                        )
                        
                        # Calculate relevance score
                        relevance_score = calculate_relevance_score(
                            article,
                            primary_keywords=PRIMARY_KEYWORDS,
                            secondary_keywords=SECONDARY_KEYWORDS,
                            required_terms=REQUIRED_TERMS,
                            excluded_terms=EXCLUDED_TERMS
                        )
                        
                        # Skip if not relevant enough
                        if relevance_score < 0.6:
                            logger.debug(f"Skipping article (low relevance): {article.content.title}")
                            continue
                        
                        # Add analysis to article
                        article.analysis = ArticleAnalysis(
                            relevance_score=relevance_score,
                            keyword_matches=self.analyzer.count_keyword_matches(
                                article.content.text,
                                PRIMARY_KEYWORDS + SECONDARY_KEYWORDS
                            )
                        )
                        
                        all_articles.append(article)
                        
                    except Exception as e:
                        logger.error(f"Error processing article {raw.get('title', 'Unknown')}: {str(e)}")
            
            except Exception as e:
                logger.error(f"Error searching source {source_config['name']}: {str(e)}")
        
        # Sort by relevance score (descending)
        all_articles.sort(key=lambda x: x.analysis.relevance_score, reverse=True)
        
        # Return top articles
        return all_articles[:limit]
    
    def process_articles(self, articles: List[Article]) -> List[Article]:
        """
        Process and analyze articles in depth.
        
        Args:
            articles: List of articles to process
            
        Returns:
            List of processed articles with full analysis
        """
        processed_articles = []
        
        for article in articles:
            try:
                # Generate summary
                summary = self.analyzer.generate_summary(article.content.text)
                
                # Extract key findings
                key_findings = self.analyzer.extract_key_findings(article.content.text)
                
                # Extract economic indicators and AI adoption metrics
                economic_indicators = self.analyzer.extract_economic_indicators(article.content.text)
                ai_adoption_metrics = self.analyzer.extract_ai_adoption_metrics(article.content.text)
                
                # Update article analysis
                article.analysis.summary = summary
                article.analysis.key_findings = key_findings
                article.analysis.economic_indicators = economic_indicators
                article.analysis.ai_adoption_metrics = ai_adoption_metrics
                
                # Save to storage
                self.storage.save_article(article)
                
                processed_articles.append(article)
                
            except Exception as e:
                logger.error(f"Error processing article {article.content.title}: {str(e)}")
        
        return processed_articles
    
    def get_stored_articles(self, days: int = 7) -> List[Article]:
        """
        Retrieve stored articles from the past N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of stored articles
        """
        return self.storage.get_recent_articles(days)
