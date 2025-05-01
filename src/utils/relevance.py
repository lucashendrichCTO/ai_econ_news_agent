"""
Relevance scoring utilities for the AI Economic Research News Agent.

This module provides functions for calculating the relevance of articles
to the agent's search criteria.
"""

from typing import List, Dict, Any
from loguru import logger

from src.models.article import Article
from config.settings import RELEVANCE_WEIGHTS


def calculate_relevance_score(
    article: Article,
    primary_keywords: List[str],
    secondary_keywords: List[str],
    required_terms: List[str] = None,
    excluded_terms: List[str] = None
) -> float:
    """
    Calculate a relevance score for an article based on keyword matches.
    
    Args:
        article: Article to score
        primary_keywords: Primary keywords to match
        secondary_keywords: Secondary keywords to match
        required_terms: Terms that must be present
        excluded_terms: Terms that must not be present
        
    Returns:
        Relevance score between 0 and 1
    """
    # Initialize score components
    title_score = 0.0
    content_score = 0.0
    source_score = 0.0
    recency_score = 0.0
    
    # Get lowercase text for matching
    title = article.content.title.lower()
    content = article.content.text.lower()
    
    # Check for required terms
    if required_terms:
        for term in required_terms:
            if term.lower() not in content and term.lower() not in title:
                logger.debug(f"Article missing required term: {term}")
                return 0.0
    
    # Check for excluded terms
    if excluded_terms:
        for term in excluded_terms:
            if term.lower() in content or term.lower() in title:
                logger.debug(f"Article contains excluded term: {term}")
                return 0.0
    
    # Calculate title score
    title_matches_primary = sum(1 for kw in primary_keywords if kw.lower() in title)
    title_matches_secondary = sum(1 for kw in secondary_keywords if kw.lower() in title)
    
    # Title with primary keywords is highly relevant
    if title_matches_primary > 0:
        title_score = min(1.0, title_matches_primary * 0.4 + title_matches_secondary * 0.1)
    else:
        title_score = min(1.0, title_matches_secondary * 0.2)
    
    # Calculate content score
    content_matches_primary = sum(1 for kw in primary_keywords if kw.lower() in content)
    content_matches_secondary = sum(1 for kw in secondary_keywords if kw.lower() in content)
    
    # Normalize by content length
    word_count = max(1, len(content.split()))
    content_density = (content_matches_primary * 2 + content_matches_secondary) / (word_count / 1000)
    
    # A density of 10+ matches per 1000 words is considered highly relevant
    content_score = min(1.0, content_density / 10)
    
    # Calculate source quality score
    source_score = article.source.quality_score
    
    # Calculate recency score (if publication date is available)
    if article.metadata.published_date:
        import datetime
        days_old = (datetime.datetime.now() - article.metadata.published_date).days
        # Newer articles get higher scores
        recency_score = max(0.0, 1.0 - (days_old / 30))  # Linear decay over 30 days
    else:
        # Default to middle score if date unknown
        recency_score = 0.5
    
    # Combine scores using weights from settings
    combined_score = (
        title_score * RELEVANCE_WEIGHTS['title_match'] +
        content_score * RELEVANCE_WEIGHTS['content_match'] +
        source_score * RELEVANCE_WEIGHTS['source_quality'] +
        recency_score * RELEVANCE_WEIGHTS['recency']
    )
    
    logger.debug(f"Relevance score for '{article.content.title}': {combined_score:.2f}")
    logger.debug(f"  Title: {title_score:.2f}, Content: {content_score:.2f}, Source: {source_score:.2f}, Recency: {recency_score:.2f}")
    
    return combined_score
