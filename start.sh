#!/bin/bash
# Start Scouter Authentication Server

echo "🔐 Starting Scouter Authentication Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please create one first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Start MailHog for email testing
echo "📧 Starting MailHog for email testing..."
if command -v mailhog >/dev/null 2>&1; then
    # Check if MailHog is already running
    if ! pgrep -f "mailhog" > /dev/null; then
        mailhog &
        sleep 2
        echo "✅ MailHog started successfully"
        echo "📬 MailHog Web UI: http://localhost:8025"
    else
        echo "✅ MailHog is already running"
    fi
else
    echo "⚠️  MailHog not found. Install with: brew install mailhog"
    echo "   Emails will not be captured during development"
fi

# Skip monitoring startup for now (Docker is causing hangs)
# Metrics will still be available at /metrics endpoint
echo ""
echo "📊 Monitoring: Skipped (start manually with: docker compose up -d)"
echo ""

# FOOLPROOF PORT CLEANUP - Kill everything on 5000 and 5001
echo "🧹 Cleaning up ports 5000 and 5001..."

# Kill port 5000
lsof -ti:5000 2>/dev/null | xargs kill -9 2>/dev/null
# Kill port 5001  
lsof -ti:5001 2>/dev/null | xargs kill -9 2>/dev/null

# Kill any existing Flask/Python processes running auth_server.py
pkill -9 -f "python.*auth_server.py" 2>/dev/null
pkill -9 -f "flask.*run" 2>/dev/null

# Wait for ports to be released
sleep 3

echo "✅ Ports cleaned up"

# Always use port 5001 (5000 often conflicts with macOS AirPlay)
PORT=5001

# Start the authentication server
echo ""
echo "🚀 Starting authentication server on http://localhost:$PORT"
echo "📱 Scouter will be available at: http://localhost:$PORT/index.html"
echo "📊 Metrics available at: http://localhost:$PORT/metrics"
echo "💡 Magic links will appear in this terminal (development mode)"
echo ""
echo "🔗 Quick Links:"
echo "   • Scouter App: http://localhost:$PORT/index.html"
echo "   • Metrics API: http://localhost:$PORT/metrics"
echo "   • MailHog: http://localhost:8025"
echo ""

# Set the port as an environment variable and start the server in background
export FLASK_PORT=$PORT
nohup python -c "
import os
from auth_server import app
port = int(os.environ.get('FLASK_PORT', 5000))
app.run(host='0.0.0.0', port=port, debug=True)
" > flask.log 2>&1 &

# Wait for server to start
sleep 3

# Check if server actually started
if lsof -i:$PORT >/dev/null 2>&1; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Scouter is running!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📋 View logs: tail -f flask.log"
    echo "🛑 Stop server: pkill -f auth_server.py"
    echo ""
else
    echo ""
    echo "❌ Server failed to start. Check flask.log for errors:"
    echo "   tail flask.log"
    exit 1
fi