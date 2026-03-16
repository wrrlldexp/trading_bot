#!/bin/bash

# Comprehensive Testing Suite for Adaptive Grid Trading Bot
# Tests backend API, frontend, database, and business logic

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "\n${BOLD}${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}ADAPTIVE GRID TRADING BOT - COMPREHENSIVE TESTS${NC}"
echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════${NC}\n"

# Test 1: Check if Docker is running
echo -e "${BLUE}[TEST 1]${NC} Checking Docker status..."
if docker ps > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC} Docker is running"
else
    echo -e "${RED}❌ FAIL${NC} Docker is not running"
    exit 1
fi

# Test 2: Check if containers are running
echo -e "\n${BLUE}[TEST 2]${NC} Checking container status..."
cd "$PROJECT_ROOT"

RUNNING_CONTAINERS=$(docker-compose ps --services 2>/dev/null || echo "")
if [ -z "$RUNNING_CONTAINERS" ]; then
    echo -e "${YELLOW}⚠️  WARNING${NC} No containers running. Starting them..."
    docker-compose up -d
    sleep 10
fi

CONTAINER_COUNT=$(docker-compose ps -q 2>/dev/null | wc -l)
if [ "$CONTAINER_COUNT" -ge 3 ]; then
    echo -e "${GREEN}✅ PASS${NC} Containers running ($CONTAINER_COUNT found)"
else
    echo -e "${RED}❌ FAIL${NC} Not enough containers running"
fi

# Test 3: Check backend health
echo -e "\n${BLUE}[TEST 3]${NC} Testing backend health..."
for i in {1..5}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC} Backend is healthy"
        break
    elif [ $i -lt 5 ]; then
        echo -e "${YELLOW}⏳ Retry $i/5...${NC}"
        sleep 2
    else
        echo -e "${RED}❌ FAIL${NC} Backend not responding"
    fi
done

# Test 4: Check frontend health
echo -e "\n${BLUE}[TEST 4]${NC} Testing frontend health..."
for i in {1..5}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC} Frontend is running"
        break
    elif [ $i -lt 5 ]; then
        echo -e "${YELLOW}⏳ Retry $i/5...${NC}"
        sleep 2
    else
        echo -e "${RED}❌ FAIL${NC} Frontend not responding"
    fi
done

# Test 5: Check database connection
echo -e "\n${BLUE}[TEST 5]${NC} Testing database connection..."
if docker-compose exec -T postgres pg_isready -U trader > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC} Database is running"
else
    echo -e "${RED}❌ FAIL${NC} Database connection failed"
fi

# Test 6: Run API tests
echo -e "\n${BLUE}[TEST 6]${NC} Running API endpoint tests..."
if command -v python3 > /dev/null 2>&1; then
    if [ -f "$PROJECT_ROOT/tests/test_system.py" ]; then
        python3 "$PROJECT_ROOT/tests/test_system.py"
    else
        echo -e "${YELLOW}⚠️  WARNING${NC} Test script not found"
    fi
else
    echo -e "${YELLOW}⚠️  WARNING${NC} Python3 not found, skipping API tests"
fi

# Test 7: Check API endpoints with curl
echo -e "\n${BLUE}[TEST 7]${NC} Testing API endpoints with curl..."

# Test health endpoint
echo -e "  • Testing /api/health..."
HEALTH=$(curl -s http://localhost:8000/api/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "    ${GREEN}✅ /api/health${NC}"
else
    echo -e "    ${RED}❌ /api/health${NC}"
fi

# Test strategies endpoint
echo -e "  • Testing /api/strategies..."
STRATEGIES=$(curl -s http://localhost:8000/api/strategies)
if echo "$STRATEGIES" | grep -q "\["; then
    echo -e "    ${GREEN}✅ /api/strategies${NC}"
else
    echo -e "    ${RED}❌ /api/strategies${NC}"
fi

# Test orders endpoint
echo -e "  • Testing /api/orders..."
ORDERS=$(curl -s http://localhost:8000/api/orders)
if echo "$ORDERS" | grep -q "\["; then
    echo -e "    ${GREEN}✅ /api/orders${NC}"
else
    echo -e "${RED}❌ /api/orders${NC}"
fi

# Test trades endpoint
echo -e "  • Testing /api/trades..."
TRADES=$(curl -s http://localhost:8000/api/trades)
if echo "$TRADES" | grep -q "\["; then
    echo -e "    ${GREEN}✅ /api/trades${NC}"
else
    echo -e "    ${RED}❌ /api/trades${NC}"
fi

# Test 8: Database data integrity
echo -e "\n${BLUE}[TEST 8]${NC} Checking database data..."
STRATEGY_COUNT=$(docker-compose exec -T postgres psql -U trader -d trading_bot -c "SELECT COUNT(*) FROM strategies;" 2>/dev/null | grep -oP '\d+' | tail -1)
echo -e "  Strategies: $STRATEGY_COUNT"

ORDER_COUNT=$(docker-compose exec -T postgres psql -U trader -d trading_bot -c "SELECT COUNT(*) FROM orders;" 2>/dev/null | grep -oP '\d+' | tail -1)
echo -e "  Orders: $ORDER_COUNT"

TRADE_COUNT=$(docker-compose exec -T postgres psql -U trader -d trading_bot -c "SELECT COUNT(*) FROM trades;" 2>/dev/null | grep -oP '\d+' | tail -1)
echo -e "  Trades: $TRADE_COUNT"

if [ "$TRADE_COUNT" -gt 0 ]; then
    echo -e "  ${GREEN}✅ Demo data loaded successfully${NC}"
else
    echo -e "  ${YELLOW}⚠️  Demo data might not be loaded${NC}"
fi

# Test 9: Check logs for errors
echo -e "\n${BLUE}[TEST 9]${NC} Checking logs for errors..."
BACKEND_ERRORS=$(docker-compose logs backend 2>/dev/null | grep -i "error" | wc -l)
if [ "$BACKEND_ERRORS" -eq 0 ]; then
    echo -e "  ${GREEN}✅ No errors in backend logs${NC}"
else
    echo -e "  ${YELLOW}⚠️  Found $BACKEND_ERRORS potential errors${NC}"
fi

# Summary
echo -e "\n${BOLD}${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}TEST SUMMARY${NC}"
echo -e "${BOLD}${BLUE}════════════════════════════════════════════════════════════${NC}\n"

echo -e "Backend API:     ${GREEN}http://localhost:8000${NC}"
echo -e "Frontend:        ${GREEN}http://localhost:3000${NC}"
echo -e "API Docs:        ${GREEN}http://localhost:8000/docs${NC}"
echo -e "Database:        ${GREEN}PostgreSQL (port 5432)${NC}"
echo -e "Cache:           ${GREEN}Redis (port 6379)${NC}"

echo -e "\n${BOLD}Available Commands:${NC}"
echo -e "  • View logs:    ${YELLOW}./scripts/logs.sh${NC}"
echo -e "  • Stop bot:     ${YELLOW}./scripts/stop.sh${NC}"
echo -e "  • Reset data:   ${YELLOW}./scripts/reset.sh${NC}"
echo -e "  • Restart:      ${YELLOW}docker-compose restart${NC}"

echo -e "\n${BOLD}Next Steps:${NC}"
echo -e "  1. Open ${BLUE}http://localhost:3000${NC} in your browser"
echo -e "  2. View API docs at ${BLUE}http://localhost:8000/docs${NC}"
echo -e "  3. Check demo data in the dashboard"
echo -e "  4. Create a new strategy"
echo -e "  5. Start the bot"

echo -e "\n${BOLD}${GREEN}All tests completed!${NC}\n"
