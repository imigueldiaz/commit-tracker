#!/bin/bash
set -e

# Wait for a moment to ensure everything is ready
sleep 2

# Remove existing database if it exists
rm -f /app/instance/commit_tracker.db

# Initialize the database
flask db upgrade

# Import initial data
python import_data.py

# Start the Flask application
exec flask run --host=0.0.0.0
