"""
Configuration settings for the AI Economic Research News Agent.
"""

# General settings
PROJECT_NAME = "AI Economic Research News Agent"
VERSION = "0.1.0"
DEBUG = True

# Search settings
ARTICLES_PER_DAY = 5
MIN_ARTICLE_LENGTH = 500  # words
MAX_ARTICLE_AGE = 7  # days

# Keywords and filters
PRIMARY_KEYWORDS = [
    "AI adoption",
    "artificial intelligence economy",
    "economic impact of AI",
    "AI economic research",
    "machine learning economy",
    "generative AI",
    "large language models",
    "AI productivity",
    "AI ROI",
    "AI transformation",
    "neural networks economy",
    "deep learning business"
]

SECONDARY_KEYWORDS = [
    "productivity gains",
    "economic growth",
    "labor market",
    "automation",
    "industry transformation",
    "ROI",
    "investment",
    "cost reduction",
    "efficiency",
    "market analysis",
    "economic forecast",
    "business impact",
    "AI startups",
    "AI funding",
    "AI implementation",
    "AI strategy",
    "AI workforce",
    "AI skills gap",
    "AI regulation",
    "AI governance"
]

REQUIRED_TERMS = ["economic", "research", "AI"]

EXCLUDED_TERMS = [
    "press release",
    "sponsored content",
    "advertisement",
]

# Relevance scoring weights
RELEVANCE_WEIGHTS = {
    "title_match": 0.3,
    "content_match": 0.4,
    "source_quality": 0.2,
    "recency": 0.1,
}

# Output settings
OUTPUT_FORMATS = ["markdown", "json"]
DEFAULT_OUTPUT_FORMAT = "markdown"
EXPORT_DIRECTORY = "../data/processed"

# Notification settings
ENABLE_EMAIL_NOTIFICATIONS = True
EMAIL_RECIPIENTS = ["lucas.hendrich@fortegrp.com"]
EMAIL_SUBJECT_TEMPLATE = "AI Economic Research: Daily Findings ({date})"

# API rate limiting
REQUEST_DELAY = 1.0  # seconds between requests
MAX_REQUESTS_PER_MINUTE = 30

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "../data/agent.log"
