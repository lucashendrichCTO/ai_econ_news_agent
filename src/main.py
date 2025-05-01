"""
AI Economic Research News Agent

Main entry point for the agent that finds economic research news about AI adoption.
"""

import os
import sys
import time
import schedule
import datetime
from loguru import logger
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import agent components
from src.agents.news_agent import AIEconomicNewsAgent
from src.utils.notification import send_email_notification
from src.utils.export import export_findings
from config.settings import (
    ARTICLES_PER_DAY,
    LOG_LEVEL,
    LOG_FILE,
    ENABLE_EMAIL_NOTIFICATIONS,
    EMAIL_RECIPIENTS,
    EMAIL_SUBJECT_TEMPLATE,
    DEFAULT_OUTPUT_FORMAT
)

# Configure logging
logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL)
logger.add(LOG_FILE, rotation="1 day", retention="30 days", level=LOG_LEVEL)

# Load environment variables
load_dotenv()


def run_agent():
    """
    Execute the AI Economic News Agent to find and process articles.
    """
    logger.info("Starting AI Economic Research News Agent")
    
    try:
        # Initialize the agent
        agent = AIEconomicNewsAgent()
        
        # Find relevant articles
        articles = agent.find_articles(limit=ARTICLES_PER_DAY)
        
        if not articles:
            logger.warning("No relevant articles found today")
            return
        
        logger.info(f"Found {len(articles)} relevant articles")
        
        # Process and analyze the articles
        processed_articles = agent.process_articles(articles)
        
        # Export the findings
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        export_path = export_findings(
            processed_articles, 
            format=DEFAULT_OUTPUT_FORMAT,
            filename=f"ai_economic_research_{today}"
        )
        
        logger.info(f"Exported findings to {export_path}")
        
        # Send email notification if enabled
        if ENABLE_EMAIL_NOTIFICATIONS:
            email_subject = EMAIL_SUBJECT_TEMPLATE.format(date=today)
            send_email_notification(
                recipients=EMAIL_RECIPIENTS,
                subject=email_subject,
                articles=processed_articles,
                export_path=export_path
            )
            logger.info(f"Sent email notification to {', '.join(EMAIL_RECIPIENTS)}")
        
        return processed_articles
        
    except Exception as e:
        logger.error(f"Error running agent: {str(e)}")
        raise


def schedule_agent():
    """
    Schedule the agent to run daily at 8:00 AM.
    """
    schedule.every().day.at("08:00").do(run_agent)
    
    logger.info("Agent scheduled to run daily at 8:00 AM")
    
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        schedule_agent()
    else:
        run_agent()
