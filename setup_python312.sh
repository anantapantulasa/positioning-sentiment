#!/bin/bash

# Setup script for Python 3.12 (recommended for compatibility)

echo "Setting up with Python 3.12..."

# Check if Python 3.12 is available
if ! command -v python3.12 &> /dev/null; then
    echo "Python 3.12 not found. Please install it first:"
    echo "  macOS: brew install python@3.12"
    echo "  Or download from: https://www.python.org/downloads/"
    exit 1
fi

cd backend

# Remove old venv if it exists
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi

# Create new venv with Python 3.12
echo "Creating virtual environment with Python 3.12..."
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete! To activate the environment, run:"
echo "  cd backend"
echo "  source venv/bin/activate"

