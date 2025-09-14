#!/bin/bash

# Digital Ocean Deployment Script for StormCommand

echo "StormCommand Deployment Script"
echo "==============================="

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app import init_db; init_db()"

# For production with gunicorn
echo "Starting Gunicorn server..."
gunicorn --bind 0.0.0.0:8000 --workers 4 wsgi:app