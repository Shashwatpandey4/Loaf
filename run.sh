#!/bin/bash
# Script to run both the API server and UI server

echo "=========================================="
echo "Starting Loaf Application"
echo "=========================================="
echo ""
echo "API Server: http://localhost:8000"
echo "UI Server:  http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "=========================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $API_PID $UI_PID 2>/dev/null
    exit
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start API server in background
echo "Starting API server on port 8000..."
cd "$(dirname "$0")"
python api_server.py &
API_PID=$!

# Wait a moment for API server to start
sleep 2

# Start UI server in background
echo "Starting UI server on port 8080..."
cd UI
python -m http.server 8080 &
UI_PID=$!

echo ""
echo "Both servers are running!"
echo "Open http://localhost:8080 in your browser"
echo ""

# Wait for both processes
wait $API_PID $UI_PID
