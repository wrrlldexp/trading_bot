#!/bin/bash

# Start the crypto trading bot using Docker Compose

echo "🚀 Starting Adaptive Grid Trading Bot..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
EOF
    echo "⚠️  Please update .env file with your Binance API credentials"
fi

# Build and start containers
echo "🐳 Building and starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo "🏥 Checking service health..."

# Check backend
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend is ready at http://localhost:8000"
else
    echo "⚠️  Backend is starting, please wait..."
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is ready at http://localhost:3000"
else
    echo "⚠️  Frontend is starting, please wait..."
fi

# Check database
if docker-compose exec -T postgres pg_isready -U trader > /dev/null 2>&1; then
    echo "✅ Database is ready"
else
    echo "⚠️  Database is starting..."
fi

echo ""
echo "🎉 Trading Bot Started!"
echo ""
echo "📊 Dashboard: http://localhost:3000"
echo "🔌 API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "To stop the bot, run: ./scripts/stop.sh"
echo "To view logs, run: docker-compose logs -f"
