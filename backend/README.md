# Crypto Trading Bot - Backend

## Setup

```bash
cd backend
pip install -r requirements.txt
```

## Environment variables

Create `.env`:

```
DATABASE_URL=postgresql://trader:trader@localhost:5432/trading_bot
REDIS_URL=redis://localhost:6379/0
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
BINANCE_TESTNET=true
LOG_LEVEL=INFO
```

## Run

```bash
python main.py
```

API will be available at `http://localhost:8000`

## Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
