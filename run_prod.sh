#!/bin/bash
# Production server startup script

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Modern CMS Production Server${NC}"

# Activate virtual environment
source venv/bin/activate

# Create necessary directories
mkdir -p uploads/{images,thumbnails,files}

# Run with gunicorn
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --capture-output
