# API Reference

Complete API reference for the Adaptive Grid Trading Bot.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required (add JWT/OAuth for production).

## Response Format

All responses are JSON:

```json
{
  "data": {...},
  "error": null,
  "timestamp": "2024-03-15T10:30:00Z"
}
```

## Endpoints

### Health & Status

#### Check API Health
```http
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Adaptive Grid Trading Bot",
  "version": "1.0.0"
}
```

#### Get System Status
```http
GET /api/status
```

Response:
```json
{
  "status": "running",
  "timestamp": "2024-03-15T10:30:00Z"
}
```

---

### Strategy Management

#### Create Strategy
```http
POST /api/strategies
Content-Type: application/json

{
  "name": "BTC Grid Bot",
  "pair": "BTCUSDT",
  "grid_levels": 10,
  "grid_profit_per_trade": 0.1,
  "atr_period": 14,
  "atr_multiplier": 2.0,
  "reverse_mode": false
}
```

Response:
```json
{
  "id": 1,
  "name": "BTC Grid Bot",
  "pair": "BTCUSDT",
  "is_active": false,
  "status": "idle",
  "grid_levels": 10,
  "grid_profit_per_trade": 0.1,
  "atr_period": 14,
  "atr_multiplier": 2.0,
  "reverse_mode": false,
  "total_trades": 0,
  "total_profit": 0.0,
  "win_rate": 0.0,
  "roi": 0.0,
  "created_at": "2024-03-15T10:30:00Z",
  "updated_at": "2024-03-15T10:30:00Z"
}
```

#### List All Strategies
```http
GET /api/strategies
```

Response:
```json
[
  {
    "id": 1,
    "name": "BTC Grid Bot",
    "pair": "BTCUSDT",
    "is_active": true,
    "status": "running",
    ...
  }
]
```

#### Get Strategy Details
```http
GET /api/strategies/{id}
```

Parameters:
- `id` (int, required): Strategy ID

Response:
```json
{
  "id": 1,
  "name": "BTC Grid Bot",
  ...
}
```

#### Control Strategy
```http
POST /api/strategies/{id}/control
Content-Type: application/json

{
  "action": "start"
}
```

Parameters:
- `id` (int, required): Strategy ID
- `action` (string, required): One of `start`, `stop`, `pause`, `resume`

Response:
```json
{
  "status": "success",
  "action": "start"
}
```

#### Get Strategy Orders
```http
GET /api/strategies/{id}/orders
```

Parameters:
- `id` (int, required): Strategy ID

Response:
```json
[
  {
    "id": 1,
    "exchange_order_id": "12345678901",
    "pair": "BTCUSDT",
    "side": "buy",
    "price": 45000.00,
    "quantity": 0.01,
    "filled_quantity": 0.01,
    "status": "filled",
    "average_fill_price": 45000.00,
    "commission": 0.00003,
    "is_grid_order": true,
    "created_at": "2024-03-15T10:30:00Z",
    "filled_at": "2024-03-15T10:31:00Z"
  }
]
```

#### Get Strategy Trades
```http
GET /api/strategies/{id}/trades
```

Parameters:
- `id` (int, required): Strategy ID

Response:
```json
[
  {
    "id": 1,
    "pair": "BTCUSDT",
    "entry_price": 45000.00,
    "exit_price": 45045.00,
    "quantity": 0.01,
    "side": "buy",
    "status": "closed",
    "profit_loss": 4.50,
    "roi": 0.01,
    "opened_at": "2024-03-15T10:30:00Z",
    "closed_at": "2024-03-15T10:31:00Z"
  }
]
```

#### Get Strategy Portfolio
```http
GET /api/strategies/{id}/portfolio
```

Parameters:
- `id` (int, required): Strategy ID

Response:
```json
{
  "current_total_value": 1045.50,
  "btc_balance": 0.01,
  "usdt_balance": 645.50,
  "total_profit": 45.50,
  "roi": 4.55,
  "max_drawdown": 2.3,
  "active_trades": 1,
  "active_orders": 3,
  "total_trades": 15,
  "win_rate": 80.0
}
```

#### Get Strategy Statistics
```http
GET /api/strategies/{id}/stats
```

Parameters:
- `id` (int, required): Strategy ID

Response:
```json
{
  "total_trades": 15,
  "total_profit": 45.50,
  "win_rate": 80.0,
  "roi": 4.55,
  "active_orders": 3,
  "active_trades": 1,
  "max_drawdown": 2.3,
  "uptime_seconds": 3600
}
```

---

### Orders

#### List All Orders
```http
GET /api/orders?skip=0&limit=100&status=open
```

Parameters:
- `skip` (int, optional): Offset, default 0
- `limit` (int, optional): Max results, default 100
- `status` (string, optional): Filter by status (open, filled, cancelled)

Response:
```json
[
  {
    "id": 1,
    "exchange_order_id": "12345678901",
    "pair": "BTCUSDT",
    "side": "buy",
    "price": 45000.00,
    "quantity": 0.01,
    "filled_quantity": 0.01,
    "status": "filled",
    ...
  }
]
```

#### Get Order Details
```http
GET /api/orders/{id}
```

Parameters:
- `id` (int, required): Order ID

Response:
```json
{
  "id": 1,
  "exchange_order_id": "12345678901",
  "pair": "BTCUSDT",
  "side": "buy",
  "price": 45000.00,
  ...
}
```

---

### Trades

#### List All Trades
```http
GET /api/trades?skip=0&limit=100&status=closed
```

Parameters:
- `skip` (int, optional): Offset, default 0
- `limit` (int, optional): Max results, default 100
- `status` (string, optional): Filter by status (open, closed)

Response:
```json
[
  {
    "id": 1,
    "pair": "BTCUSDT",
    "entry_price": 45000.00,
    "exit_price": 45045.00,
    ...
  }
]
```

#### Get Trade Details
```http
GET /api/trades/{id}
```

Parameters:
- `id` (int, required): Trade ID

Response:
```json
{
  "id": 1,
  "pair": "BTCUSDT",
  "entry_price": 45000.00,
  "exit_price": 45045.00,
  ...
}
```

---

### Portfolio

#### Get Portfolio History
```http
GET /api/portfolio-history?strategy_id=1&skip=0&limit=100
```

Parameters:
- `strategy_id` (int, required): Strategy ID
- `skip` (int, optional): Offset, default 0
- `limit` (int, optional): Max results, default 100

Response:
```json
[
  {
    "total_value": 1045.50,
    "btc_balance": 0.01,
    "usdt_balance": 645.50,
    "total_profit": 45.50,
    "roi": 4.55,
    "max_drawdown": 2.3,
    "timestamp": "2024-03-15T10:30:00Z"
  }
]
```

---

## Error Handling

Error responses include status code and message:

```json
{
  "detail": "Strategy not found"
}
```

Common error codes:
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

---

## Rate Limiting

No rate limits currently applied. For production, implement:
- 100 requests/minute per IP
- 10000 requests/day per IP

---

## Examples

### Create and start a strategy

```bash
# Create strategy
curl -X POST http://localhost:8000/api/strategies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "BTC Grid Bot",
    "pair": "BTCUSDT",
    "grid_levels": 10,
    "grid_profit_per_trade": 0.1
  }'

# Start strategy (replace ID with response id)
curl -X POST http://localhost:8000/api/strategies/1/control \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'
```

### Get strategy performance

```bash
curl http://localhost:8000/api/strategies/1/stats
```

### Monitor orders in real-time

```bash
# Watch for updates
while true; do
  curl http://localhost:8000/api/strategies/1/orders
  sleep 5
done
```

---

## WebSocket Support

For real-time updates, connect to WebSocket endpoint (future enhancement):

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/strategy/1');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Order update:', data);
};
```

---

## SDK Support

Future SDKs:
- Python SDK
- JavaScript/TypeScript SDK
- Go SDK

---

Last updated: March 15, 2024
