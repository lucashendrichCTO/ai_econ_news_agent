"""
Production deployment script for AI Economic News Agent.
This script sets up and runs the application in production mode.
"""
import os
import sys
import subprocess
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('deploy_production')

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = ['NEWS_API_KEY', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file")
        return False
    
    return True

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import gunicorn
        logger.info("Gunicorn is installed")
    except ImportError:
        logger.error("Gunicorn is not installed. Installing now...")
        subprocess.run([sys.executable, "-m", "pip", "install", "gunicorn"], check=True)
        logger.info("Gunicorn installed successfully")
    
    # Check if other dependencies are installed
    try:
        import flask
        import openai
        import requests
        import feedparser
        import dotenv
        logger.info("All required dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Please run: pip install -r requirements.txt")
        return False

def create_logs_directory():
    """Create logs directory if it doesn't exist."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir()
        logger.info("Created logs directory")
    return True

def run_production_server(port=8000, workers=4):
    """Run the production server using Gunicorn."""
    logger.info(f"Starting production server on port {port} with {workers} workers")
    
    # Build the command
    cmd = [
        "gunicorn",
        "--workers", str(workers),
        "--bind", f"0.0.0.0:{port}",
        "--log-level", "info",
        "--access-logfile", "logs/access.log",
        "--error-logfile", "logs/error.log",
        "production:app"
    ]
    
    # Run the server
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        logger.info(f"Server will be available at http://localhost:{port}")
        logger.info("Press Ctrl+C to stop the server")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start production server: {e}")
        return False
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    
    return True

def main():
    """Main entry point for the deployment script."""
    parser = argparse.ArgumentParser(description="Deploy AI Economic News Agent in production mode")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--workers", type=int, default=4, help="Number of Gunicorn workers")
    args = parser.parse_args()
    
    logger.info("Starting production deployment")
    
    # Run checks
    if not check_environment():
        return 1
    
    if not check_dependencies():
        return 1
    
    if not create_logs_directory():
        return 1
    
    # Run the server
    success = run_production_server(port=args.port, workers=args.workers)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
