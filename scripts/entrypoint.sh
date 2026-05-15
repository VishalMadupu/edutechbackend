#!/bin/sh

# Run the table creation script
echo "Initializing database..."
python scripts/create_tables.py

# Start the application
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
