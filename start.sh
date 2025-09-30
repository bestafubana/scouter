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

# Start Prometheus for metrics (optional)
echo ""
echo "📊 Starting Prometheus for metrics..."
if command -v prometheus >/dev/null 2>&1; then
    # Check if Prometheus is already running
    if ! pgrep -f "prometheus" > /dev/null; then
        # Check if prometheus.yml exists
        if [ -f "prometheus.yml" ]; then
            prometheus --config.file=prometheus.yml --web.listen-address=":9090" > prometheus.log 2>&1 &
            sleep 2
            echo "✅ Prometheus started successfully"
            echo "📈 Prometheus UI: http://localhost:9090"
            echo "📊 Metrics endpoint: http://localhost:5001/metrics"
        else
            echo "⚠️  prometheus.yml not found. Creating default config..."
            cat > prometheus.yml <<'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'scouter'
    static_configs:
      - targets: ['localhost:5001']
    metrics_path: '/metrics'
    scrape_interval: 5s
EOF
            prometheus --config.file=prometheus.yml --web.listen-address=":9090" > prometheus.log 2>&1 &
            sleep 2
            echo "✅ Prometheus started with default config"
            echo "📈 Prometheus UI: http://localhost:9090"
        fi
    else
        echo "✅ Prometheus is already running"
    fi
else
    echo "⚠️  Prometheus not found. Install with: brew install prometheus"
    echo "   Metrics will still be available at /metrics endpoint"
fi

# Start Grafana for dashboards (optional)
echo ""
echo "📈 Starting Grafana for dashboards..."
if command -v grafana-server >/dev/null 2>&1; then
    # Check if Grafana is already running
    if ! pgrep -f "grafana-server" > /dev/null; then
        # macOS: Use brew services if available
        if command -v brew >/dev/null 2>&1; then
            brew services start grafana >/dev/null 2>&1
            sleep 2
            echo "✅ Grafana started successfully"
            echo "📊 Grafana UI: http://localhost:3000 (admin/admin)"
        else
            # Linux: Start directly
            grafana-server --homepath=/usr/share/grafana > grafana.log 2>&1 &
            sleep 2
            echo "✅ Grafana started successfully"
            echo "📊 Grafana UI: http://localhost:3000 (admin/admin)"
        fi
    else
        echo "✅ Grafana is already running"
    fi
else
    echo "⚠️  Grafana not found. Install with: brew install grafana"
    echo "   You can still use Prometheus to query metrics"
fi

# Function to kill processes on a port more aggressively
kdill_port_processes() {
    local port=$1
    echo "🔍 Checking for existing processes on port $port..."
    
    # Try multiple methods to find and kill processes
    PIDS=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$PIDS" ]; then
        echo "⚡ Killing processes on port $port: $PIDS"
        echo $PIDS | xargs kill -9 2>/dev/null
        sleep 2
    fi
    
    # Double-check with netstat as backup
    NETSTAT_PIDS=$(netstat -tulpn 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d/ -f1 | grep -v -)
    if [ ! -z "$NETSTAT_PIDS" ]; then
        echo "⚡ Found additional processes via netstat: $NETSTAT_PIDS"
        echo $NETSTAT_PIDS | xargs kill -9 2>/dev/null
        sleep 1
    fi
}

# Try to clean up port 5000
kill_port_processes 5000

# Check if port 5000 is still in use
if lsof -i:5000 >/dev/null 2>&1; then
    echo "⚠️  Port 5000 is still in use (possibly by system service like AirPlay)"
    echo "🔄 Switching to port 5001..."
    PORT=5001
    kill_port_processes 5001
else
    PORT=5000
fi

# Start the authentication server
echo ""
echo "🚀 Starting authentication server on http://localhost:$PORT"
echo "📱 Scouter will be available at: http://localhost:$PORT/index.html"
echo "📊 Metrics available at: http://localhost:$PORT/metrics"
echo "💡 Magic links will appear in this terminal (development mode)"
echo ""
echo "🔗 Quick Links:"
echo "   • Scouter App: http://localhost:$PORT/index.html"
echo "   • MailHog: http://localhost:8025"
if command -v prometheus >/dev/null 2>&1 && pgrep -f "prometheus" > /dev/null; then
    echo "   • Prometheus: http://localhost:9090"
fi
if command -v grafana-server >/dev/null 2>&1 && pgrep -f "grafana-server" > /dev/null; then
    echo "   • Grafana: http://localhost:3000"
fi
echo ""
echo "🛑 Press Ctrl+C to stop all services"
echo ""

# Set the port as an environment variable and start the server
export FLASK_PORT=$PORT
python -c "
import os
from auth_server import app
port = int(os.environ.get('FLASK_PORT', 5000))
app.run(host='0.0.0.0', port=port, debug=True)
" 