#!/bin/bash

# Check if venv exists and set up if missing
if [ ! -d "venv" ]; then
    echo "🛠️ Virtual environment 'venv' not found. Creating..."
    python3 -m venv venv || { echo "❌ Failed to create virtual environment"; exit 1; }
    echo "✅ Virtual environment created!"
    
    echo "📦 Installing 'requests' in the virtual environment..."
    ./venv/bin/pip install requests || { echo "❌ Failed to install requests"; exit 1; }
    echo "✅ 'requests' installed!"
fi

# Run the script using the virtual environment's Python
./venv/bin/python ghost.py || { echo "❌ Script execution failed"; exit 1; }