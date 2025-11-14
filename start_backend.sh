#!/bin/bash

# Start Backend Server
echo "Starting Gold Trading Signal Backend..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Check for GROQ_API_KEY
if [ -z "$GROQ_API_KEY" ]; then
    echo "WARNING: GROQ_API_KEY environment variable is not set!"
    echo "Please set it with: export GROQ_API_KEY='your-api-key'"
    exit 1
fi

# Start server
echo "Starting FastAPI server on http://localhost:8000"
python main.py

