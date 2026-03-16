from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Supports three modes:
    - DEMO_MODE=true: Uses dummy data, no API calls
    - BINANCE_TESTNET=true: Uses Binance testnet with real API
    - BINANCE_TESTNET=false: Uses live Binance (requires real API keys)
    """
    
    # ===== Application Settings =====
    APP_NAME: str = "Adaptive Grid Trading Bot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    DEMO_MODE: bool = True  # Demo mode without real API keys

    # ===== Database Configuration =====
    DATABASE_URL: str = "postgresql://trader:trader@localhost:5432/trading_bot"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ===== Binance Exchange Settings =====
    BINANCE_API_KEY: str = "demo"
    BINANCE_API_SECRET: str = "demo"
    BINANCE_TESTNET: bool = True  # Use testnet by default for safety
    
    # ===== Trading Parameters =====
    TRADING_PAIR: str = "BTCUSDT"
    INITIAL_INVESTMENT: float = 1000.0
    
    # ===== Grid Strategy Configuration =====
    GRID_LEVELS: int = 10
    GRID_PROFIT_PER_TRADE: float = 0.1  # 0.1% profit per trade
    ATR_PERIOD: int = 14  # Period for Average True Range calculation
    ATR_MULTIPLIER: float = 2.0  # Multiplier for grid step calculation
    
    # ===== Risk Management Settings =====
    MAX_POSITION_SIZE: float = 50.0  # Max % of portfolio per position
    MAX_DRAWDOWN: float = 20.0  # Max allowed % drawdown
    MAX_ACTIVE_ORDERS: int = 20  # Max concurrent orders
    EMERGENCY_STOP: bool = False  # Trigger emergency stop on max drawdown
    
    # ===== Logging Configuration =====
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
