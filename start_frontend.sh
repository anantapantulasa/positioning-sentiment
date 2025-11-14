#!/bin/bash

# Start Frontend Server
echo "Starting Gold Trading Signal Frontend..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start development server
echo "Starting Vite dev server on http://localhost:3000"
npm run dev

