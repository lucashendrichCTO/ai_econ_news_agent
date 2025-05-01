"""
Simple production server runner for AI Economic News Agent.
Uses Waitress for production deployment on Windows.
"""
import os
import sys
import logging
from dotenv import load_dotenv
from waitress import serve
from src.web.simple_app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('production_server')

# Load environment variables
load_dotenv()

def main():
    """Run the production server."""
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    
    # Configure server
    port = int(os.environ.get('PORT', 8000))
    threads = int(os.environ.get('THREADS', 4))
    
    # Log server info
    logger.info("=== AI Economic News Agent Production Server ===")
    logger.info(f"Starting server on port {port} with {threads} threads")
    logger.info(f"Server will be available at http://localhost:{port}")
    logger.info("Press Ctrl+C to stop the server")
    
    # Run the server
    try:
        serve(app, host='0.0.0.0', port=port, threads=threads)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
