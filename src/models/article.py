"""
Article model for the AI Economic Research News Agent.
"""

from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, HttpUrl


class ArticleSource(BaseModel):
    """Model representing the source of an article."""
    name: str
    url: HttpUrl
    quality_score: float = Field(ge=0.0, le=1.0)
    type: str = "website"  # website, research, aggregator, etc.


class ArticleContent(BaseModel):
    """Model representing the content of an article."""
    title: str
    text: str
    html: Optional[str] = None
    word_count: int = 0
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.text and not self.word_count:
            self.word_count = len(self.text.split())


class ArticleMetadata(BaseModel):
    """Model representing metadata about an article."""
    authors: List[str] = []
    published_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    categories: List[str] = []
    tags: List[str] = []


class ArticleAnalysis(BaseModel):
    """Model representing analysis of an article."""
    relevance_score: float = Field(ge=0.0, le=1.0)
    keyword_matches: Dict[str, int] = {}
    sentiment: Optional[float] = None
    summary: Optional[str] = None
    key_findings: List[str] = []
    economic_indicators: List[Dict[str, str]] = []
    ai_adoption_metrics: List[Dict[str, str]] = []


class Article(BaseModel):
    """
    Model representing a news article about AI economic research.
    """
    id: Optional[str] = None
    url: HttpUrl
    source: ArticleSource
    content: ArticleContent
    metadata: ArticleMetadata
    analysis: Optional[ArticleAnalysis] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            # Generate a simple ID based on title and date
            title_part = self.content.title.lower().replace(' ', '-')[:30]
            date_part = datetime.now().strftime("%Y%m%d")
            self.id = f"{date_part}-{title_part}"
