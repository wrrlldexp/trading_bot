#!/bin/bash

# View logs

echo "📋 Trading Bot Logs"
echo "===================="
echo ""
echo "🔵 Backend logs:"
docker-compose logs -f backend
