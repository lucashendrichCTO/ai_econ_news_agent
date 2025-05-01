"""
Article storage service for the AI Economic Research News Agent.

This module implements the storage functionality for saving and retrieving articles.
"""

import os
import json
import pickle
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from src.services.protocols import StorageProtocol
from src.models.article import Article


class ArticleStorage(StorageProtocol):
    """
    Article storage service for saving and retrieving articles.
    
    Implements the StorageProtocol interface.
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the article storage.
        
        Args:
            storage_dir: Directory to store articles in
        """
        if storage_dir is None:
            # Default to data/articles directory relative to project root
            self.storage_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data', 'articles'
            )
        else:
            self.storage_dir = storage_dir
        
        # Create directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Create index file if it doesn't exist
        self.index_file = os.path.join(self.storage_dir, 'index.json')
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'w') as f:
                json.dump([], f)
        
        logger.info(f"Article storage initialized at {self.storage_dir}")
    
    def save_article(self, article: Article) -> bool:
        """
        Save an article to storage.
        
        Args:
            article: Article to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate filename from article ID
            filename = f"{article.id}.pkl"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Save article as pickle
            with open(filepath, 'wb') as f:
                pickle.dump(article, f)
            
            # Update index
            self._update_index(article)
            
            logger.info(f"Saved article: {article.content.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving article: {str(e)}")
            return False
    
    def get_article(self, article_id: str) -> Optional[Article]:
        """
        Retrieve an article from storage.
        
        Args:
            article_id: ID of the article to retrieve
            
        Returns:
            Article if found, None otherwise
        """
        try:
            # Generate filepath from article ID
            filename = f"{article_id}.pkl"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Check if file exists
            if not os.path.exists(filepath):
                logger.warning(f"Article not found: {article_id}")
                return None
            
            # Load article from pickle
            with open(filepath, 'rb') as f:
                article = pickle.load(f)
            
            return article
            
        except Exception as e:
            logger.error(f"Error retrieving article {article_id}: {str(e)}")
            return None
    
    def list_articles(self, filters: Dict[str, Any] = None) -> List[Article]:
        """
        List articles in storage, optionally filtered.
        
        Args:
            filters: Dictionary of filters to apply
            
        Returns:
            List of articles
        """
        try:
            # Load index
            index = self._load_index()
            
            # Apply filters if provided
            if filters:
                filtered_index = []
                for item in index:
                    match = True
                    for key, value in filters.items():
                        if key in item and item[key] != value:
                            match = False
                            break
                    if match:
                        filtered_index.append(item)
                index = filtered_index
            
            # Load articles
            articles = []
            for item in index:
                article = self.get_article(item['id'])
                if article:
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error listing articles: {str(e)}")
            return []
    
    def get_recent_articles(self, days: int = 7) -> List[Article]:
        """
        Get articles from the past N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of articles
        """
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Load index
            index = self._load_index()
            
            # Filter by date
            recent_index = [
                item for item in index 
                if 'date' in item and datetime.fromisoformat(item['date']) >= cutoff_date
            ]
            
            # Load articles
            articles = []
            for item in recent_index:
                article = self.get_article(item['id'])
                if article:
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error getting recent articles: {str(e)}")
            return []
    
    def _load_index(self) -> List[Dict[str, Any]]:
        """Load the article index."""
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            return []
    
    def _update_index(self, article: Article):
        """
        Update the article index with a new or updated article.
        
        Args:
            article: Article to add or update in the index
        """
        try:
            # Load current index
            index = self._load_index()
            
            # Check if article already exists in index
            for i, item in enumerate(index):
                if item['id'] == article.id:
                    # Update existing entry
                    index[i] = self._create_index_entry(article)
                    break
            else:
                # Add new entry
                index.append(self._create_index_entry(article))
            
            # Save updated index
            with open(self.index_file, 'w') as f:
                json.dump(index, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating index: {str(e)}")
    
    def _create_index_entry(self, article: Article) -> Dict[str, Any]:
        """
        Create an index entry for an article.
        
        Args:
            article: Article to create index entry for
            
        Returns:
            Dictionary with index entry data
        """
        # Get publication date or current date as fallback
        date = article.metadata.published_date or datetime.now()
        
        return {
            'id': article.id,
            'title': article.content.title,
            'source': article.source.name,
            'url': str(article.url),
            'date': date.isoformat(),
            'relevance_score': article.analysis.relevance_score if article.analysis else 0.0
        }
