# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Adaptive Grid Trading Bot                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐       ┌──────────────┐      ┌──────────┐   │
│  │  Dashboard   │       │  Web API     │      │ Broker   │   │
│  │   (Next.js)  │◄─────►│  (FastAPI)   │◄────►│ (Binance)│   │
│  └──────────────┘       └──────────────┘      └──────────┘   │
│         ▲                      ▲                      ▲         │
│         │                      │                      │         │
│      Browser               REST API              WebSocket      │
│                                                                 │
│       Frontend               Backend               Exchange     │
│                                                                 │
│  ┌─────────────┐      ┌────────────────┐                       │
│  │   Zustand   │      │   PostgreSQL   │                       │
│  │   (Store)   │      │   (Database)   │                       │
│  └─────────────┘      └────────────────┘                       │
│         ▲                      ▲                                │
│         │                      │                               │
│      State Mgmt         Data Persistence                        │
│                                                                 │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
                    Docker Compose
                          │
        ┌───────────────┬──┴──┬───────────────┐
        │               │     │               │
    PostgreSQL       Redis   Backend       Frontend
      (DB)          (Cache)  (Python)      (Node.js)
```

## Module Breakdown

### 1. Exchange Integration Layer

**File**: `backend/app/exchange/`

#### Components:
- **BinanceClient**: REST API wrapper
  - Authentication with API keys
  - Order placement (limit orders)
  - Order cancellation
  - Balance retrieval
  - Order status checking

- **BinanceWebSocket**: Real-time market data
  - Ticker updates (24h stats)
  - Trade stream (price updates)
  - Kline stream (candlesticks)
  - Order book updates

#### Data Flow:
```
Binance API
    ▲
    │ REST (place orders, check status)
    │
    ├─────────────────────────┐
    │                         │
BinanceClient          BinanceWebSocket
    │                         │
    │ Sync                    │ Async
    │                         │
    └────────────┬────────────┘
                 │
            Backend App
                 │
        Strategy Engine
```

### 2. Strategy Engine

**File**: `backend/app/strategies/adaptive_grid.py`

#### Classes:

**ATRCalculator**
```python
calculate(high[], low[], close[], period=14) -> float
```
Computes volatility using Average True Range.

**AdaptiveGridStrategy**
```python
generate_grid(center_price, atr, balance) -> List[GridLevel]
detect_grid_break() -> bool
get_next_orders() -> List[Order]
```

Logic:
1. Calculate ATR from last 14 candles
2. Grid step = ATR × 2.0 (configurable)
3. Generate buy orders below center, sell orders above
4. Monitor price movement
5. Rebuild grid if price leaves boundaries

**ReverseStrategy** (Optional)
- Trend-following mode
- EMA-based trend detection
- Buy on downtrend, sell on uptrend

#### Grid Example:
```
Price = $45,000
ATR = $200
Step = $200 × 2.0 = $400

SELL Orders:        BUY Orders:
$45,800  (qty)      $44,200  (qty)
$46,200  (qty)      $43,800  (qty)
$46,600  (qty)      $43,400  (qty)
```

### 3. Order Manager

**File**: `backend/app/core/order_manager.py`

#### Responsibilities:
- Create orders on exchange
- Track order status
- Cancel orders
- Refresh all open orders
- Store orders in database

#### Workflow:
```
create_order()
    │
    ├─► Place on Binance
    │
    ├─► Store in DB
    │
    └─► Return Order object

update_order_status()
    │
    ├─► Query exchange
    │
    ├─► Update filled qty
    │
    ├─► Mark as filled
    │
    └─► Commit to DB
```

### 4. Risk Manager

**File**: `backend/app/core/risk_manager.py`

#### Checks:
1. **Position Size**: Order value < 50% portfolio
2. **Max Orders**: Active orders < 20
3. **Drawdown**: Current DD < 20% max
4. **Emergency**: Stop if any limit breached

#### Risk Calculation:
```
Position Size = (Quantity × Price) / Portfolio Value
               < 50% ✓

Drawdown = (Peak Value - Current Value) / Peak Value
         < 20% ✓

Emergency Stop = triggered if any check fails
```

### 5. Analytics Engine

**File**: `backend/app/analytics/analytics_engine.py`

#### Metrics:

**ROI (Return on Investment)**
```
ROI% = ((Final Balance - Initial Balance) / Initial Balance) × 100
```

**Win Rate**
```
Win Rate% = (Winning Trades / Total Trades) × 100
```

**Max Drawdown**
```
Max DD% = (Peak Value - Lowest Value) / Peak Value × 100
```

**Sharpe Ratio**
```
Sharpe = (Mean Return - Risk Free Rate) / Std Dev × √252
```

**P&L Calculation**
```
P&L = Exit Price - Entry Price × Quantity
ROI% = P&L / (Entry Price × Quantity) × 100
```

### 6. Portfolio Tracker

**File**: `backend/app/analytics/analytics_engine.py` (PortfolioTracker class)

#### Functions:
- **take_snapshot()**: Record portfolio state
- **get_history()**: Retrieve past snapshots
- **get_overview()**: Current portfolio summary

#### Data:
```
Snapshot {
  total_value: USDT balance + (BTC balance × BTC price)
  btc_balance: amount of BTC held
  usdt_balance: amount of USDT held
  roi: calculated return
  max_drawdown: historical drawdown
  timestamp: when recorded
}
```

### 7. Database Models

**File**: `backend/app/models/models.py`

```
Strategy
├─ id (PK)
├─ name
├─ pair (BTCUSDT)
├─ is_active
├─ status (idle/running/paused)
├─ grid parameters
├─ risk parameters
├─ statistics (total_profit, win_rate, roi)
└─ Relationships:
   ├─ orders (1:Many)
   ├─ trades (1:Many)
   └─ portfolio_snapshots (1:Many)

Order
├─ id (PK)
├─ strategy_id (FK)
├─ exchange_order_id
├─ side (BUY/SELL)
├─ price, quantity
├─ status (open/filled/cancelled)
├─ filled_quantity, average_fill_price
└─ is_grid_order, grid_level

Trade
├─ id (PK)
├─ strategy_id (FK)
├─ entry_price, exit_price
├─ quantity, side
├─ profit_loss, roi
├─ opened_at, closed_at
└─ status (open/closed)

PortfolioSnapshot
├─ id (PK)
├─ strategy_id (FK)
├─ total_value
├─ btc_balance, usdt_balance
├─ total_profit, roi
├─ max_drawdown
└─ timestamp

GridLevel
├─ id (PK)
├─ strategy_id (FK)
├─ level number
├─ price
├─ side (BUY/SELL)
├─ is_filled
└─ filled_at
```

### 8. API Routes

**File**: `backend/app/routes/`

#### Strategy Routes
```
POST   /api/strategies                    Create strategy
GET    /api/strategies                    List all
GET    /api/strategies/{id}              Get one
POST   /api/strategies/{id}/control      Start/stop/pause
GET    /api/strategies/{id}/orders       Get orders
GET    /api/strategies/{id}/trades       Get trades
GET    /api/strategies/{id}/portfolio    Get portfolio
GET    /api/strategies/{id}/stats        Get stats
```

#### Trade Routes
```
GET    /api/orders                       All orders
GET    /api/orders/{id}                 Get order
GET    /api/trades                       All trades
GET    /api/trades/{id}                 Get trade
GET    /api/portfolio-history            Portfolio history
```

#### Health Routes
```
GET    /api/health                       Health check
GET    /api/status                       System status
```

### 9. Frontend Architecture

**File**: `frontend/`

#### Pages:
```
pages/
├─ index.tsx               Dashboard (strategy list)
├─ strategy/[id].tsx      Strategy detail page
└─ _app.tsx              App wrapper with QueryClient
```

#### Hooks (TanStack Query):
```
useStrategies()           Get all strategies
useStrategy(id)          Get one strategy
useOrders()              Get all orders
useStrategyOrders(id)    Get strategy orders
useTrades()              Get all trades
useStrategyTrades(id)    Get strategy trades
usePortfolio(id)         Get portfolio data
useHealth()              Health check
```

#### Components:
- Strategy cards
- Order table
- Trade list
- Portfolio stats
- Control buttons

#### State Management:
```
Zustand Store (appStore.ts)
├─ selectedStrategy
└─ setSelectedStrategy()
```

### 10. Data Flow Example

```
User clicks "Start Strategy"
        │
        ▼
Frontend: /api/strategies/{id}/control
        │
        ▼
Backend: POST control endpoint
        │
        ▼
Strategy status = "running"
        │
        ▼
Market Data Stream Starts
        │
        ▼
Price Update from WebSocket
        │
        ▼
Strategy detects price at grid level
        │
        ▼
Risk Manager checks limits ✓
        │
        ▼
Order Manager places order on Binance
        │
        ▼
Order stored in PostgreSQL
        │
        ▼
Frontend refreshes via TanStack Query
        │
        ▼
User sees new order in Dashboard
```

### 11. Database Flow

```
Strategy Created
        │
        ▼
INSERT strategies table
        │
        ├─► Generate Grid
        │       │
        │       ▼
        │   INSERT grid_levels
        │
        ├─► Market Data Updates
        │       │
        │       ▼
        │   INSERT price_history
        │
        ├─► Order Placed
        │       │
        │       ▼
        │   INSERT orders
        │       │
        │       ▼
        │   UPDATE orders (status update)
        │
        ├─► Trade Closed
        │       │
        │       ▼
        │   INSERT trades
        │       │
        │       ▼
        │   UPDATE strategies (stats)
        │
        └─► Portfolio Snapshot
                │
                ▼
            INSERT portfolio_snapshots
```

### 12. Deployment Topology

```
┌─────────────────────────────────────────────────────┐
│              Docker Compose Network                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  postgres:5432     redis:6379   backend:8000    │
│       │                  │            │          │
│       │◄─────────────────┼────────────┤          │
│       │                  │            │          │
│       └──────────────────┼────────────┘          │
│                          │                        │
│                     frontend:3000                  │
│                          │                        │
│                   (Next.js server)                 │
│                                                    │
└─────────────────────────────────────────────────────┘
          │
          │ Exposed Ports
          │
    ┌─────┴─────────────────────────┐
    │                               │
  8000                            3000
  (API)                        (Dashboard)
```

---

## Summary

This architecture provides:

✅ **Modularity**: Each component has single responsibility
✅ **Scalability**: Async operations, Redis caching
✅ **Reliability**: Database persistence, error handling
✅ **Maintainability**: Clear separation of concerns
✅ **Testability**: Independent modules easy to test
✅ **Security**: API key isolation, input validation
✅ **Observability**: Logging at all levels

All components work together to provide a professional-grade crypto trading platform.
