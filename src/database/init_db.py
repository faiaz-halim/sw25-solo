#!/usr/bin/env python3
"""
Database initialization script to create tables.
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database.database import init_db
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize the database tables."""
    try:
        logger.info("Initializing database tables...")
        init_db()
        logger.info("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
