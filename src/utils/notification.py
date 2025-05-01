"""
Notification utilities for the AI Economic Research News Agent.

This module provides functionality for sending notifications about new findings.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Optional
from loguru import logger

from src.models.article import Article


def send_email_notification(
    recipients: List[str],
    subject: str,
    articles: List[Article],
    export_path: Optional[str] = None
) -> bool:
    """
    Send an email notification with the latest findings.
    
    Args:
        recipients: List of email addresses to send to
        subject: Email subject
        articles: List of processed articles to include
        export_path: Optional path to an export file to attach
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if SMTP settings are configured
        smtp_server = os.environ.get("SMTP_SERVER")
        smtp_port = os.environ.get("SMTP_PORT")
        smtp_username = os.environ.get("SMTP_USERNAME")
        smtp_password = os.environ.get("SMTP_PASSWORD")
        sender_email = os.environ.get("SENDER_EMAIL")
        
        if not all([smtp_server, smtp_port, smtp_username, smtp_password, sender_email]):
            logger.error("SMTP settings not configured. Cannot send email notification.")
            return False
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        # Create email body
        body = create_email_body(articles)
        msg.attach(MIMEText(body, 'html'))
        
        # Attach export file if provided
        if export_path and os.path.exists(export_path):
            with open(export_path, 'rb') as file:
                attachment = MIMEApplication(file.read(), Name=os.path.basename(export_path))
                attachment['Content-Disposition'] = f'attachment; filename="{os.path.basename(export_path)}"'
                msg.attach(attachment)
        
        # Send email
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending email notification: {str(e)}")
        return False


def create_email_body(articles: List[Article]) -> str:
    """
    Create the HTML body for the email notification.
    
    Args:
        articles: List of processed articles
        
    Returns:
        HTML formatted email body
    """
    html = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; }
            .article { margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
            .title { font-size: 18px; font-weight: bold; color: #333; }
            .source { font-size: 14px; color: #666; margin-bottom: 10px; }
            .summary { margin-bottom: 15px; }
            .findings { margin-bottom: 15px; }
            .finding-item { margin-bottom: 5px; }
            .metrics { font-size: 14px; color: #444; }
            .relevance { font-weight: bold; color: #0066cc; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h2>AI Economic Research: Latest Findings</h2>
        <p>The AI Economic News Agent has found the following relevant articles:</p>
    """
    
    for article in articles:
        html += f"""
        <div class="article">
            <div class="title"><a href="{article.url}">{article.content.title}</a></div>
            <div class="source">Source: {article.source.name} | Quality Score: {article.source.quality_score:.1f}</div>
        """
        
        if article.analysis and article.analysis.summary:
            html += f"""
            <div class="summary">
                <strong>Summary:</strong><br>
                {article.analysis.summary}
            </div>
            """
        
        if article.analysis and article.analysis.key_findings:
            html += """
            <div class="findings">
                <strong>Key Findings:</strong><br>
                <ul>
            """
            
            for finding in article.analysis.key_findings[:5]:  # Limit to top 5 findings
                html += f"""<li class="finding-item">{finding}</li>"""
            
            html += """
                </ul>
            </div>
            """
        
        if article.analysis:
            html += f"""
            <div class="metrics">
                <span class="relevance">Relevance Score: {article.analysis.relevance_score:.2f}</span> | 
                Word Count: {article.content.word_count}
            </div>
            """
        
        html += """
        </div>
        """
    
    html += """
        <p>This is an automated notification from the AI Economic Research News Agent.</p>
    </body>
    </html>
    """
    
    return html
