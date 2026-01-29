#!/bin/bash
# Development server startup script

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Modern CMS Development Server${NC}"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -r requirements.txt --quiet

# Create .env from example if not exists
if [ ! -f ".env" ]; then
    echo -e "${GREEN}Creating .env file...${NC}"
    cp .env.example .env
fi

# Create necessary directories
mkdir -p uploads/{images,thumbnails,files}
mkdir -p static/{css,js,images}

# Run the server
echo -e "${BLUE}Starting server on http://localhost:8000${NC}"
echo -e "${BLUE}API Docs: http://localhost:8000/docs${NC}"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
