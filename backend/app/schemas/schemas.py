from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class TradeStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


# === STRATEGY SCHEMAS ===

class StrategyParamsUpdate(BaseModel):
    grid_levels: Optional[int] = None
    grid_profit_per_trade: Optional[float] = None
    atr_period: Optional[int] = None
    atr_multiplier: Optional[float] = None
    max_position_size: Optional[float] = None
    max_drawdown: Optional[float] = None
    max_active_orders: Optional[int] = None
    reverse_mode: Optional[bool] = None


class StrategyCreate(BaseModel):
    name: str
    pair: str = "BTCUSDT"
    grid_levels: int = 10
    grid_profit_per_trade: float = 0.1
    atr_period: int = 14
    atr_multiplier: float = 2.0
    reverse_mode: bool = False


class StrategyResponse(BaseModel):
    id: int
    name: str
    pair: str
    is_active: bool
    status: str
    grid_levels: int
    grid_profit_per_trade: float
    atr_period: int
    atr_multiplier: float
    reverse_mode: bool
    total_trades: int
    total_profit: float
    win_rate: float
    roi: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# === ORDER SCHEMAS ===

class OrderCreate(BaseModel):
    pair: str
    side: OrderSide
    price: float
    quantity: float
    grid_level: Optional[int] = None


class OrderResponse(BaseModel):
    id: int
    exchange_order_id: Optional[str]
    pair: str
    side: OrderSide
    price: float
    quantity: float
    filled_quantity: float
    status: str
    average_fill_price: float
    commission: float
    is_grid_order: bool
    created_at: datetime
    filled_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# === TRADE SCHEMAS ===

class TradeResponse(BaseModel):
    id: int
    pair: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    side: OrderSide
    status: TradeStatus
    profit_loss: float
    roi: float
    opened_at: datetime
    closed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# === PORTFOLIO SCHEMAS ===

class PortfolioSnapshot(BaseModel):
    total_value: float
    btc_balance: float
    usdt_balance: float
    total_profit: float
    roi: float
    max_drawdown: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class PortfolioOverview(BaseModel):
    current_total_value: float
    btc_balance: float
    usdt_balance: float
    total_profit: float
    roi: float
    max_drawdown: float
    active_trades: int
    active_orders: int
    total_trades: int
    win_rate: float


# === GRID LEVEL SCHEMAS ===

class GridLevelResponse(BaseModel):
    level: int
    price: float
    side: OrderSide
    is_filled: bool
    filled_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# === CONTROL SCHEMAS ===

class StrategyControl(BaseModel):
    action: str  # start, stop, pause, resume


class StrategyStats(BaseModel):
    total_trades: int
    total_profit: float
    win_rate: float
    roi: float
    active_orders: int
    active_trades: int
    max_drawdown: float
    uptime_seconds: int
