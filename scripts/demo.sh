#!/bin/bash

# Quick demo start without Binance API keys

echo "🎨 Starting in DEMO MODE (no API keys needed)..."
echo ""

# Create .env for demo
cat > .env << 'EOF'
BINANCE_API_KEY=demo
BINANCE_API_SECRET=demo
BINANCE_TESTNET=true
DEBUG=false
DEMO_MODE=true
LOG_LEVEL=INFO
EOF

echo "✅ Created .env in demo mode"
echo ""

# Make scripts executable
chmod +x scripts/start.sh

echo "🚀 Starting Docker Compose..."
echo ""

# Start with docker-compose
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

# Check health
echo ""
echo "🏥 Checking services..."
echo ""

if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend ready: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
else
    echo "⚠️  Backend still starting, wait a moment..."
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend ready: http://localhost:3000"
else
    echo "⚠️  Frontend still starting, wait a moment..."
fi

echo ""
echo "════════════════════════════════════════════"
echo "🎉 DEMO MODE IS READY!"
echo "════════════════════════════════════════════"
echo ""
echo "📊 Dashboard:  http://localhost:3000"
echo "🔌 API:        http://localhost:8000"
echo "📚 API Docs:   http://localhost:8000/docs"
echo ""
echo "✨ You can now:"
echo "   • View the demo strategy on dashboard"
echo "   • See demo orders and trades"
echo "   • Check portfolio analytics"
echo "   • Review API responses"
echo ""
echo "🛑 To stop: docker-compose down"
echo "📋 To view logs: docker-compose logs -f backend"
echo ""
