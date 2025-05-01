"""
Production server for AI Economic News Agent.
Uses Gunicorn for production deployment.
"""
import os
from dotenv import load_dotenv
from src.web.simple_app import app

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    # This file is used for running with Gunicorn
    # Command: gunicorn -w 4 -b 0.0.0.0:8000 production:app
    pass
