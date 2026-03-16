#!/bin/bash

# Quick start guide for Adaptive Grid Trading Bot

echo "════════════════════════════════════════════════════════"
echo "  Adaptive Grid Trading Bot - Quick Start"
echo "════════════════════════════════════════════════════════"
echo ""

echo "📋 Prerequisites:"
echo "  ✓ Docker & Docker Compose installed"
echo "  ✓ Binance account with API keys"
echo "  ✓ 2GB+ disk space"
echo ""

echo "🚀 Quick Start Steps:"
echo ""
echo "1️⃣  Configure environment:"
echo "   cp .env.example .env"
echo "   nano .env  # Add your Binance API keys"
echo ""

echo "2️⃣  Start the bot:"
echo "   chmod +x scripts/start.sh"
echo "   ./scripts/start.sh"
echo ""

echo "3️⃣  Access services:"
echo "   Dashboard:   http://localhost:3000"
echo "   API:         http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo ""

echo "4️⃣  Create your first strategy:"
echo "   - Go to http://localhost:3000"
echo "   - Click 'Create Strategy'"
echo "   - Configure: Name, Pair (BTCUSDT), Grid Levels (10)"
echo "   - Click 'Create'"
echo ""

echo "5️⃣  Start trading:"
echo "   - Select strategy from dashboard"
echo "   - Click 'Start Strategy'"
echo "   - Monitor in real-time"
echo ""

echo "📊 Monitoring:"
echo "   View logs:     ./scripts/logs.sh"
echo "   Stop bot:      ./scripts/stop.sh"
echo "   Reset data:    ./scripts/reset.sh"
echo ""

echo "⚠️  Important:"
echo "   • Always start with BINANCE_TESTNET=true"
echo "   • Start with small amounts"
echo "   • Monitor regularly"
echo "   • Never commit .env with real keys"
echo ""

echo "📚 Documentation:"
echo "   • README.md - Full documentation"
echo "   • ARCHITECTURE.md - System design"
echo "   • Backend: backend/README.md"
echo "   • Frontend: frontend/README.md"
echo ""

echo "════════════════════════════════════════════════════════"
echo "Let's get started! 🚀"
echo "════════════════════════════════════════════════════════"
