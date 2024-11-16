# Database Directory

This directory contains the empty database template with the correct schema structure.

- `empty.db`: Empty SQLite database with all tables created. This file should be used as a template when setting up a new instance of the application.

## How to use

When setting up a new instance of the application:

1. Copy `empty.db` to `instance/commit-tracker.db`
2. Start the application

## Schema Updates

If you need to update the database schema:

1. Make your changes to the models
2. Run `create_empty_db.py` to generate a new empty database with the updated schema
3. Test the new schema
4. If everything works, commit the new `empty.db` to the repository
