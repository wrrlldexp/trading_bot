#!/bin/bash

# Quick Test Script - Check system status
echo "🧪 QUICK SYSTEM TEST"
echo "===================="

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed"
    exit 1
fi
echo "✅ Docker installed"

# Check if project directory exists
if [ ! -d "/Users/magomedkuriev/Desktop/Новая папка/trading_bot" ]; then
    echo "❌ Project directory not found"
    exit 1
fi
echo "✅ Project directory found"

# Check files exist
cd "/Users/magomedkuriev/Desktop/Новая папка/trading_bot"

if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found"
    exit 1
fi
echo "✅ docker-compose.yml found"

if [ ! -f "backend/main.py" ]; then
    echo "❌ backend/main.py not found"
    exit 1
fi
echo "✅ backend/main.py found"

if [ ! -f "frontend/src/pages/index.tsx" ]; then
    echo "❌ frontend/src/pages/index.tsx not found"
    exit 1
fi
echo "✅ frontend/src/pages/index.tsx found"

# Check configuration
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    exit 1
fi
echo "✅ .env file found"

echo ""
echo "📊 PROJECT STRUCTURE"
echo "===================="
echo "Backend modules:"
find backend/app -name "*.py" -type f | wc -l | xargs echo "  - Python files:"

echo "Frontend modules:"
find frontend/src -name "*.tsx" -o -name "*.ts" | wc -l | xargs echo "  - TypeScript files:"

echo "Configuration files:"
ls -1 frontend/ | grep -E "config|json|js$" | wc -l | xargs echo "  - Config files:"

echo ""
echo "✅ ALL CHECKS PASSED"
