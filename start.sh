#!/bin/bash
echo "================================================"
echo "  F1 2026 - Race Intelligence Dashboard"
echo "================================================"

cd "$(dirname "$0")"
echo ""
echo "Checking dependencies..."

if ! pip show flask > /dev/null 2>&1; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies."
        exit 1
    fi
fi

echo ""
echo "Starting Flask server at http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

# Open browser (works on both Linux and macOS)
if command -v xdg-open > /dev/null 2>&1; then
    # Linux
    (sleep 1 && xdg-open "http://localhost:5000") &
elif command -v open > /dev/null 2>&1; then
    # macOS
    (sleep 1 && open "http://localhost:5000") &
fi

python app.py
