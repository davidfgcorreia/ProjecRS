#!/bin/bash
# Clean and re-initialize the test database for a fresh test run

set -e

# Remove the SQLite test database file if it exists
if [ -f ./test.db ]; then
    echo "Removing old test.db..."
    rm ./test.db
fi

# Recreate all tables using SQLAlchemy
python3 -c 'from app.db.database import Base, engine; import app.models; Base.metadata.create_all(bind=engine)'

echo "Test database reset and initialized."
