"""
Simple production-ready server for AI Economic News Agent.
Uses Flask's built-in server with production settings.
"""
import os
import sys
import logging
from dotenv import load_dotenv

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
    
    # Log server info
    logger.info("=== AI Economic News Agent Production Server ===")
    logger.info(f"Starting server on port {port}")
    logger.info(f"Server will be available at http://localhost:{port}")
    logger.info("Press Ctrl+C to stop the server")
    
    # Import the app here to avoid circular imports
    from src.web.simple_app import app
    
    # Run the server
    try:
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
