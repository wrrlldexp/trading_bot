# Adaptive Grid Trading Bot

A **modern, production-ready cryptocurrency trading system** implementing an **Adaptive Grid Trading Strategy** on Binance.

**Status**: ✅ Full system setup complete

## 🎯 Features

✅ **Adaptive Grid Strategy**
- Volatility-based grid generation using ATR
- Automatic grid boundary adjustment
- Support for reverse trend-following mode

✅ **Exchange Integration**
- Binance REST API + WebSocket streams
- Real-time price updates
- Order management and tracking

✅ **Risk Management**
- Position size limits
- Drawdown protection
- Maximum active orders limits
- Emergency stop mechanism

✅ **Analytics & Reporting**
- P&L calculations
- ROI tracking
- Win rate statistics
- Sharpe ratio computation
- Portfolio snapshots

✅ **Modern Dashboard**
- Real-time order visualization
- Trade history with filters
- Portfolio analytics
- Strategy controls
- Grid visualization

✅ **Professional Setup**
- Docker Compose with PostgreSQL + Redis
- Production-ready FastAPI backend
- Modern Next.js frontend
- Database migrations
- Logging and error handling

---

## 🏗️ Architecture

```
trading-bot/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── exchange/        # Binance API client
│   │   ├── strategies/      # Trading strategies
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routes/          # API endpoints
│   │   ├── core/            # Config, DB, logger, managers
│   │   └── analytics/       # Analytics engine
│   ├── main.py             # FastAPI app entry
│   └── requirements.txt     # Python dependencies
│
├── frontend/                # Next.js dashboard
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Next.js pages
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utilities (API client)
│   │   ├── types/           # TypeScript types
│   │   └── store/           # Zustand store
│   ├── package.json
│   └── next.config.js
│
├── docker/
│   ├── Dockerfile.backend   # Backend container
│   └── Dockerfile.frontend  # Frontend container
│
├── docker-compose.yml       # Full stack setup
├── scripts/
│   ├── start.sh            # Start the bot
│   ├── stop.sh             # Stop the bot
│   ├── logs.sh             # View logs
│   └── reset.sh            # Reset all data
│
└── README.md (this file)

```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Binance account with API keys (get from https://www.binance.com/en/account/api-management)
- 2GB+ available disk space
- macOS/Linux (or WSL on Windows)

### 1. Clone & Setup

```bash
cd /path/to/workspace
```

### 2. Configure Environment

Create `.env` file in root directory:

```env
BINANCE_API_KEY=your_actual_api_key
BINANCE_API_SECRET=your_actual_secret
BINANCE_TESTNET=true
```

⚠️ **IMPORTANT**: Use testnet first! Change `BINANCE_TESTNET=false` only in production.

### 3. Start the Bot

```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

This will:
- Start PostgreSQL database
- Start Redis cache
- Build and run FastAPI backend
- Build and run Next.js frontend
- Initialize the database
- Run health checks

### 4. Access Services

```
📊 Dashboard:      http://localhost:3000
🔌 API:            http://localhost:8000
📚 API Docs:       http://localhost:8000/docs (Swagger)
🔍 API ReDoc:      http://localhost:8000/redoc
```

### 5. Create First Strategy

1. Go to http://localhost:3000
2. Click "Create Strategy"
3. Configure:
   - Name: "BTC Grid Bot"
   - Pair: "BTCUSDT"
   - Grid Levels: 10
   - Grid Profit: 0.1%
   - ATR Period: 14
   - ATR Multiplier: 2.0
4. Click "Create"

### 6. Start Trading

1. Select your strategy from dashboard
2. Click "Start Strategy"
3. Monitor orders and trades in real-time
4. View analytics and portfolio value

---

## 📋 System Architecture

### Backend (FastAPI + Python)

**Core Modules:**

1. **Exchange Integration Layer** (`app/exchange/`)
   - `binance_client.py`: REST API wrapper
   - `websocket_stream.py`: Real-time market data

2. **Strategy Engine** (`app/strategies/`)
   - `adaptive_grid.py`: Grid generation, ATR calculation, trend detection
   - Support for reverse mode (trend-following)

3. **Order Manager** (`app/core/order_manager.py`)
   - Order creation and cancellation
   - Status tracking and refresh
   - Grid-based order management

4. **Risk Manager** (`app/core/risk_manager.py`)
   - Position sizing checks
   - Drawdown monitoring
   - Emergency stop mechanism
   - Active orders limits

5. **Analytics Engine** (`app/analytics/`)
   - P&L calculations
   - Win rate, ROI, Sharpe ratio
   - Portfolio tracking
   - Performance metrics

6. **API Routes** (`app/routes/`)
   - `/api/strategies` - Strategy management
   - `/api/orders` - Order information
   - `/api/trades` - Trade history
   - `/api/portfolio-history` - Portfolio snapshots

### Frontend (Next.js + React)

**Pages:**
- `/` - Dashboard with strategy overview
- `/strategy/[id]` - Strategy details, orders, trades

**Components:**
- Strategy cards and statistics
- Order table (real-time)
- Trade history with filters
- Portfolio charts

**Data Management:**
- TanStack Query for API calls
- Zustand for client state
- TypeScript for type safety

### Database (PostgreSQL)

**Tables:**
- `strategies` - Trading strategies
- `orders` - Exchange orders
- `trades` - Executed trades
- `portfolio_snapshots` - Historical portfolio values
- `price_history` - Market data
- `grid_levels` - Grid configuration

### Message Queue (Redis)

- Order status cache
- Real-time market data
- Session management
- Background job queue

---

## 📊 Trading Strategy

### Adaptive Grid Strategy

**How it works:**

1. **Grid Generation**
   - Calculate ATR (Average True Range) from last 14 candles
   - Grid step = ATR × multiplier (default 2.0)
   - Generate buy/sell orders above and below current price

2. **Execution**
   - When price hits a buy order → execute → place sell order above
   - When price hits a sell order → execute → place buy order below
   - Repeat to capture small profits (0.1% per trade)

3. **Adaptation**
   - Monitor price movement
   - Rebuild grid if price breaks boundaries
   - Adjust step size based on volatility

### Risk Controls

- **Max Position Size**: 50% of portfolio per trade
- **Max Drawdown**: 20% portfolio decline → stop trading
- **Max Orders**: 20 concurrent orders
- **Emergency Stop**: Trigger if conditions deteriorate

---

## 🔧 API Documentation

### Create Strategy

```bash
curl -X POST http://localhost:8000/api/strategies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "BTC Grid Bot",
    "pair": "BTCUSDT",
    "grid_levels": 10,
    "grid_profit_per_trade": 0.1,
    "atr_period": 14,
    "atr_multiplier": 2.0,
    "reverse_mode": false
  }'
```

### Get Strategy

```bash
curl http://localhost:8000/api/strategies/1
```

### Start Strategy

```bash
curl -X POST http://localhost:8000/api/strategies/1/control \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'
```

### Get Orders

```bash
curl http://localhost:8000/api/strategies/1/orders
```

### Get Trades

```bash
curl http://localhost:8000/api/strategies/1/trades
```

### Get Portfolio

```bash
curl http://localhost:8000/api/strategies/1/portfolio
```

---

## 🛠️ Commands

### Start Bot
```bash
./scripts/start.sh
```

### Stop Bot
```bash
./scripts/stop.sh
```

### View Logs
```bash
./scripts/logs.sh
# or
docker-compose logs -f backend
```

### Reset Database
```bash
./scripts/reset.sh
```

### Access Database
```bash
docker-compose exec postgres psql -U trader -d trading_bot
```

### Access Redis
```bash
docker-compose exec redis redis-cli
```

---

## 📦 Dependencies

### Backend
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **psycopg2**: PostgreSQL driver
- **python-binance**: Binance API
- **pandas/numpy**: Data analysis
- **ta**: Technical analysis (ATR)
- **pydantic**: Data validation

### Frontend
- **Next.js 14**: React framework
- **React 18**: UI library
- **TailwindCSS**: Styling
- **TanStack Query**: Data fetching
- **Axios**: HTTP client
- **Zustand**: State management
- **Recharts**: Charts & visualization

---

## 🔐 Security Notes

1. **Never commit API keys** - Use `.env` file (in `.gitignore`)
2. **Use testnet first** - Always test strategies on Binance testnet
3. **Start with small amounts** - Test with minimal capital
4. **Monitor regularly** - Check logs and performance daily
5. **Backup data** - PostgreSQL data is in Docker volume

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Rebuild containers
docker-compose build --no-cache

# Check database
docker-compose logs postgres
```

### Frontend can't connect to API
```bash
# Verify backend is running
curl http://localhost:8000/api/health

# Check NEXT_PUBLIC_API_URL in docker-compose.yml
# Should be: http://backend:8000 (inside container)
# Or: http://localhost:8000 (from browser)
```

### Database connection error
```bash
# Reset database
./scripts/reset.sh

# Start fresh
./scripts/start.sh
```

### Port already in use
```bash
# Change ports in docker-compose.yml
# Or kill existing process
lsof -i :8000  # Find process on port 8000
```

---

## 📈 Performance Tips

1. **Use testnet** initially - faster, free, safe
2. **Start with 10 grid levels** - too many = high fees
3. **Use ATR multiplier 2-3** - adapts to volatility
4. **Monitor max drawdown** - stop if > 20%
5. **Review trades daily** - check for anomalies

---

## 🚀 Production Deployment

For VPS/VDS deployment:

1. **Install Docker** on server
2. **Clone repository**
3. **Set environment variables** in `.env`
4. **Configure SSL** with nginx reverse proxy
5. **Setup automatic backups** for database
6. **Monitor resource usage** (CPU, RAM, disk)
7. **Setup logging** with ELK stack or similar

Example nginx config for production (add to `/etc/nginx/sites-available/`):

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 443 ssl http2;
    server_name tradingbot.example.com;

    ssl_certificate /etc/letsencrypt/live/tradingbot.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tradingbot.example.com/privkey.pem;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📚 Further Reading

- [Binance API Documentation](https://binance-docs.github.io/apidocs/)
- [Grid Trading Strategy](https://www.investopedia.com/terms/g/grid-trading.asp)
- [Average True Range (ATR)](https://www.investopedia.com/terms/a/atr.asp)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)

---

## 📄 License

MIT License - Free for personal and commercial use

---

## ⚠️ Disclaimer

This software is provided as-is. **Use at your own risk**. The developers are not responsible for:
- Trading losses
- Account security issues
- API key compromise
- Binance service outages

**Always:**
1. Start with testnet
2. Use small amounts
3. Monitor regularly
4. Understand the strategy
5. Keep backups

---

## 📞 Support

For issues:
1. Check logs: `./scripts/logs.sh`
2. Review database: `docker-compose exec postgres psql -U trader`
3. Test API: `curl http://localhost:8000/api/health`
4. Check Docker: `docker-compose ps`

---

**Happy Trading! 🚀📈**
