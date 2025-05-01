"""
Command-line interface for the AI Economic Research News Agent.

This module provides a CLI for running the agent with various options.
"""

import os
import sys
import argparse
import datetime
from loguru import logger
from typing import List

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import agent components
from src.agents.news_agent import AIEconomicNewsAgent
from src.utils.export import export_findings
from src.utils.notification import send_email_notification
from src.models.article import Article
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


def setup_parser() -> argparse.ArgumentParser:
    """Set up the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="AI Economic Research News Agent CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Find articles command
    find_parser = subparsers.add_parser("find", help="Find relevant articles")
    find_parser.add_argument(
        "--limit", type=int, default=ARTICLES_PER_DAY,
        help="Maximum number of articles to find"
    )
    find_parser.add_argument(
        "--process", action="store_true",
        help="Process the articles after finding them"
    )
    find_parser.add_argument(
        "--export", action="store_true",
        help="Export the findings after processing"
    )
    find_parser.add_argument(
        "--notify", action="store_true",
        help="Send email notifications after processing"
    )
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Process stored articles")
    process_parser.add_argument(
        "--days", type=int, default=1,
        help="Process articles from the past N days"
    )
    process_parser.add_argument(
        "--export", action="store_true",
        help="Export the findings after processing"
    )
    process_parser.add_argument(
        "--notify", action="store_true",
        help="Send email notifications after processing"
    )
    
    # View command
    view_parser = subparsers.add_parser("view", help="View stored articles")
    view_parser.add_argument(
        "--days", type=int, default=7,
        help="View articles from the past N days"
    )
    view_parser.add_argument(
        "--export", action="store_true",
        help="Export the viewed articles"
    )
    
    # Run command (full pipeline)
    run_parser = subparsers.add_parser("run", help="Run the full agent pipeline")
    run_parser.add_argument(
        "--limit", type=int, default=ARTICLES_PER_DAY,
        help="Maximum number of articles to find"
    )
    
    return parser


def find_articles(args: argparse.Namespace) -> List[Article]:
    """Find relevant articles based on CLI arguments."""
    logger.info(f"Finding up to {args.limit} relevant articles")
    
    agent = AIEconomicNewsAgent()
    articles = agent.find_articles(limit=args.limit)
    
    logger.info(f"Found {len(articles)} relevant articles")
    
    if args.process:
        articles = process_articles(articles)
    
    if args.export and articles:
        export_articles(articles)
    
    if args.notify and articles:
        notify_articles(articles)
    
    return articles


def process_articles(articles: List[Article]) -> List[Article]:
    """Process articles for in-depth analysis."""
    if not isinstance(articles, list):
        logger.info(f"Processing articles from the past {articles.days} days")
        agent = AIEconomicNewsAgent()
        articles = agent.get_stored_articles(days=articles.days)
    
    if not articles:
        logger.warning("No articles found to process")
        return []
    
    logger.info(f"Processing {len(articles)} articles")
    
    agent = AIEconomicNewsAgent()
    processed_articles = agent.process_articles(articles)
    
    logger.info(f"Processed {len(processed_articles)} articles")
    
    return processed_articles


def view_articles(args: argparse.Namespace) -> List[Article]:
    """View stored articles based on CLI arguments."""
    logger.info(f"Viewing articles from the past {args.days} days")
    
    agent = AIEconomicNewsAgent()
    articles = agent.get_stored_articles(days=args.days)
    
    if not articles:
        logger.warning("No articles found")
        return []
    
    logger.info(f"Found {len(articles)} articles")
    
    # Print article information
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article.content.title}")
        print(f"   Source: {article.source.name}")
        if article.metadata.published_date:
            print(f"   Published: {article.metadata.published_date.strftime('%Y-%m-%d')}")
        if article.analysis and article.analysis.relevance_score:
            print(f"   Relevance: {article.analysis.relevance_score:.2f}")
        print(f"   URL: {article.url}")
    
    if args.export:
        export_articles(articles)
    
    return articles


def export_articles(articles: List[Article]) -> None:
    """Export articles to file."""
    if not articles:
        logger.warning("No articles to export")
        return
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    export_path = export_findings(
        articles,
        format=DEFAULT_OUTPUT_FORMAT,
        filename=f"ai_economic_research_{today}"
    )
    
    if export_path:
        logger.info(f"Exported findings to {export_path}")
        print(f"\nFindings exported to: {export_path}")


def notify_articles(articles: List[Article]) -> None:
    """Send email notification about articles."""
    if not ENABLE_EMAIL_NOTIFICATIONS:
        logger.warning("Email notifications are disabled in settings")
        return
    
    if not articles:
        logger.warning("No articles to notify about")
        return
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    email_subject = EMAIL_SUBJECT_TEMPLATE.format(date=today)
    
    success = send_email_notification(
        recipients=EMAIL_RECIPIENTS,
        subject=email_subject,
        articles=articles
    )
    
    if success:
        logger.info(f"Sent email notification to {', '.join(EMAIL_RECIPIENTS)}")
        print(f"\nEmail notification sent to {', '.join(EMAIL_RECIPIENTS)}")
    else:
        logger.error("Failed to send email notification")
        print("\nFailed to send email notification. Check logs for details.")


def run_agent(args: argparse.Namespace) -> None:
    """Run the full agent pipeline."""
    logger.info("Running full agent pipeline")
    
    # Find articles
    articles = find_articles(args)
    
    if not articles:
        logger.warning("No relevant articles found")
        return
    
    # Process articles
    processed_articles = process_articles(articles)
    
    # Export findings
    export_articles(processed_articles)
    
    # Send notifications
    notify_articles(processed_articles)


def main():
    """Main entry point for the CLI."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "find":
            find_articles(args)
        elif args.command == "process":
            process_articles(args)
        elif args.command == "view":
            view_articles(args)
        elif args.command == "run":
            run_agent(args)
    except Exception as e:
        logger.error(f"Error running command {args.command}: {str(e)}")
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
