#!/bin/bash
# Start Prometheus + Grafana monitoring stack with Docker

echo "🐳 Starting Scouter Monitoring Stack with Docker..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Install Docker Desktop from: https://docs.docker.com/desktop/install/mac-install/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "⚠️  Docker daemon is not running. Starting Docker Desktop..."
    open -a Docker
    
    echo "⏳ Waiting for Docker to start (this may take 10-30 seconds)..."
    
    # Wait for Docker daemon to be ready (max 60 seconds)
    for i in {1..60}; do
        if docker info &> /dev/null; then
            echo "✅ Docker is ready!"
            break
        fi
        sleep 1
        echo -n "."
    done
    
    if ! docker info &> /dev/null; then
        echo ""
        echo "❌ Docker failed to start. Please start Docker Desktop manually and try again."
        exit 1
    fi
    echo ""
fi

# Start the monitoring stack
echo "🚀 Starting Prometheus and Grafana containers..."
docker compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Monitoring stack started successfully!"
    echo ""
    echo "🔗 Access your monitoring tools:"
    echo "   📊 Prometheus: http://localhost:9090"
    echo "   📈 Grafana:    http://localhost:3000 (admin/admin)"
    echo ""
    echo "💡 Make sure Scouter is running (./start.sh) to see metrics"
    echo ""
    echo "📝 Useful commands:"
    echo "   • Stop:    docker compose down"
    echo "   • Logs:    docker compose logs -f"
    echo "   • Status:  docker compose ps"
else
    echo "❌ Failed to start monitoring stack"
    exit 1
fi

