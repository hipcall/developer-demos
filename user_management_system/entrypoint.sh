#!/bin/bash
# Create database from seed if it doesn't exist
if [ ! -f /app/data/database.db ]; then
    echo "Database not found. Restoring from seed..."
    cp /app/data/database.db.seed /app/data/database.db
else
    echo "Database already exists. Skipping restore."
fi
# Start the application
echo "Starting application..."
exec python app.py
