#!/bin/bash
# Pre-deployment setup script for Render

set -e

echo "🔧 Running pre-deployment setup..."

# Ensure database directory exists
mkdir -p data

# Run database migrations if needed
if command -v alembic &> /dev/null; then
    echo "Running database migrations..."
    alembic upgrade head
fi

# Initialize database
echo "Initializing database..."
python -c "from backend.database import init_db; init_db()"

echo "✓ Pre-deployment setup complete"
