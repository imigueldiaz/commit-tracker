#!/bin/bash
set -e

# Wait for a moment to ensure everything is ready
sleep 2

# Create instance directory if it doesn't exist
mkdir -p /app/instance

# Verify sqlite3 is available
if ! command -v sqlite3 &> /dev/null; then
    echo "Error: sqlite3 command not found"
    exit 1
fi

check_database() {
    local db_path="$1"
    echo "Running database checks on: $db_path"
    
    # Check if file exists and is not empty
    if [ ! -s "$db_path" ]; then
        echo "Database is empty or does not exist"
        return 1
    fi
    
    # Check SQLite integrity
    echo "Checking database integrity..."
    if ! /usr/bin/sqlite3 "$db_path" "PRAGMA integrity_check;" > /dev/null 2>&1; then
        echo "Database failed integrity check"
        return 2
    fi
    
    # List all tables for debugging
    echo "Listing all tables in database..."
    /usr/bin/sqlite3 "$db_path" ".tables"
    
    # Check if commit table exists with more detailed output
    echo "Checking for commit table..."
    local table_info
    table_info=$(/usr/bin/sqlite3 "$db_path" "SELECT sql FROM sqlite_master WHERE type='table' AND name='commit';" 2>/dev/null)
    if [ -n "$table_info" ]; then
        echo "Found commit table structure:"
        echo "$table_info"
        
        # Check if there are any records with error handling
        echo "Counting commits..."
        local count_result
        count_result=$(/usr/bin/sqlite3 "$db_path" "SELECT COUNT(*) FROM \"commit\";" 2>&1)
        if [ $? -ne 0 ]; then
            echo "Error counting commits: $count_result"
            return 4
        fi
        
        local record_count=$count_result
        if [ "$record_count" -gt 0 ]; then
            echo "Found $record_count commits"
            # Show some sample data
            echo "Sample commits:"
            /usr/bin/sqlite3 "$db_path" "SELECT * FROM \"commit\" LIMIT 3;"
            return 0
        else
            echo "No commits found in table"
            return 5
        fi
    else
        echo "Commit table not found in schema"
        return 3
    fi
}

init_new_database() {
    echo "Initializing new database..."
    if [ -f /app/db/empty.db ]; then
        echo "Copying template database..."
        cp /app/db/empty.db /app/instance/commit_tracker.db
    else
        echo "Creating empty database..."
        touch /app/instance/commit_tracker.db
    fi
    
    echo "Applying database migrations..."
    flask db upgrade
    
    echo "Verifying database structure..."
    /usr/bin/sqlite3 /app/instance/commit_tracker.db ".schema \"commit\""
    
    echo "Importing initial data..."
    python import_data.py
    
    echo "Verifying imported data..."
    /usr/bin/sqlite3 /app/instance/commit_tracker.db "SELECT COUNT(*) FROM \"commit\";"
}

DB_PATH="/app/instance/commit_tracker.db"

# Main database handling logic
if [ -f "$DB_PATH" ]; then
    echo "Checking existing database..."
    if check_database "$DB_PATH"; then
        echo "Database is valid and contains data"
        echo "Applying any pending migrations..."
        flask db upgrade
    else
        echo "Database needs initialization"
        rm -f "$DB_PATH"
        init_new_database
    fi
else
    echo "No database found. Creating new database..."
    init_new_database
fi

# Start the Flask application
exec flask run --host=0.0.0.0
