"""
Protocols for the AI Economic Research News Agent.

This module defines the interfaces for external service interactions following
the Model Concept Protocol (MCP) design pattern.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.models.article import Article


class NewsSourceProtocol(ABC):
    """Protocol for interacting with news sources."""
    
    @abstractmethod
    def fetch_articles(self, keywords: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch articles from the news source based on keywords.
        
        Args:
            keywords: List of keywords to search for
            limit: Maximum number of articles to fetch
            
        Returns:
            List of article data dictionaries
        """
        pass


class ContentExtractorProtocol(ABC):
    """Protocol for extracting content from web pages."""
    
    @abstractmethod
    def extract(self, url: str) -> Dict[str, Any]:
        """
        Extract content from a web page.
        
        Args:
            url: URL of the web page
            
        Returns:
            Dictionary containing extracted content
        """
        pass


class AnalysisServiceProtocol(ABC):
    """Protocol for analyzing article content."""
    
    @abstractmethod
    def analyze_relevance(self, article: Article, keywords: List[str]) -> float:
        """
        Analyze the relevance of an article to the given keywords.
        
        Args:
            article: Article to analyze
            keywords: List of keywords to check relevance against
            
        Returns:
            Relevance score between 0 and 1
        """
        pass
    
    @abstractmethod
    def generate_summary(self, article: Article) -> str:
        """
        Generate a summary of the article.
        
        Args:
            article: Article to summarize
            
        Returns:
            Summary text
        """
        pass
    
    @abstractmethod
    def extract_key_findings(self, article: Article) -> List[str]:
        """
        Extract key findings from the article.
        
        Args:
            article: Article to extract findings from
            
        Returns:
            List of key findings
        """
        pass


class StorageProtocol(ABC):
    """Protocol for storing and retrieving articles."""
    
    @abstractmethod
    def save_article(self, article: Article) -> bool:
        """
        Save an article to storage.
        
        Args:
            article: Article to save
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_article(self, article_id: str) -> Optional[Article]:
        """
        Retrieve an article from storage.
        
        Args:
            article_id: ID of the article to retrieve
            
        Returns:
            Article if found, None otherwise
        """
        pass
    
    @abstractmethod
    def list_articles(self, filters: Dict[str, Any] = None) -> List[Article]:
        """
        List articles in storage, optionally filtered.
        
        Args:
            filters: Dictionary of filters to apply
            
        Returns:
            List of articles
        """
        pass


class NotificationProtocol(ABC):
    """Protocol for sending notifications."""
    
    @abstractmethod
    def send(self, recipients: List[str], subject: str, content: str) -> bool:
        """
        Send a notification.
        
        Args:
            recipients: List of recipient addresses
            subject: Notification subject
            content: Notification content
            
        Returns:
            True if successful, False otherwise
        """
        pass
