from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class TradeStatus(str, enum.Enum):
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class OrderSide(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    pair = Column(String, default="BTCUSDT")
    is_active = Column(Boolean, default=False)
    status = Column(String, default="idle")  # idle, running, paused
    
    # Strategy parameters
    grid_levels = Column(Integer, default=10)
    grid_profit_per_trade = Column(Float, default=0.1)
    atr_period = Column(Integer, default=14)
    atr_multiplier = Column(Float, default=2.0)
    reverse_mode = Column(Boolean, default=False)
    
    # Risk parameters
    max_position_size = Column(Float, default=50.0)
    max_drawdown = Column(Float, default=20.0)
    max_active_orders = Column(Integer, default=20)
    
    # Stats
    total_trades = Column(Integer, default=0)
    total_profit = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    orders = relationship("Order", back_populates="strategy", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="strategy", cascade="all, delete-orphan")
    portfolio_snapshots = relationship("PortfolioSnapshot", back_populates="strategy", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), index=True)
    
    exchange_order_id = Column(String, unique=True, index=True, nullable=True)
    pair = Column(String, default="BTCUSDT")
    side = Column(SQLEnum(OrderSide), index=True)
    price = Column(Float)
    quantity = Column(Float)
    status = Column(String, default="open")  # open, filled, cancelled, failed
    
    filled_quantity = Column(Float, default=0.0)
    average_fill_price = Column(Float, default=0.0)
    commission = Column(Float, default=0.0)
    
    is_grid_order = Column(Boolean, default=True)
    grid_level = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    filled_at = Column(DateTime, nullable=True)
    
    # Relations
    strategy = relationship("Strategy", back_populates="orders")


class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), index=True)
    
    pair = Column(String, default="BTCUSDT")
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float)
    side = Column(SQLEnum(OrderSide))
    status = Column(SQLEnum(TradeStatus), default=TradeStatus.OPEN)
    
    profit_loss = Column(Float, default=0.0)  # Absolute PnL
    roi = Column(Float, default=0.0)  # ROI %
    
    entry_order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    exit_order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # Relations
    strategy = relationship("Strategy", back_populates="trades")


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), index=True)
    
    total_value = Column(Float)  # USDT equivalent
    btc_balance = Column(Float)
    usdt_balance = Column(Float)
    
    total_profit = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relations
    strategy = relationship("Strategy", back_populates="portfolio_snapshots")


class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    pair = Column(String, default="BTCUSDT", index=True)
    
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    
    timestamp = Column(DateTime, index=True)
    timeframe = Column(String, default="1m")  # 1m, 5m, 15m, 1h, 4h, 1d
    
    __table_args__ = (
        # Composite index for efficient queries
        # ('pair', 'timeframe', 'timestamp'),
    )


class GridLevel(Base):
    __tablename__ = "grid_levels"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), index=True)
    
    level = Column(Integer)  # Level number (0 = middle, -1 = below, +1 = above)
    price = Column(Float)
    side = Column(SQLEnum(OrderSide))
    is_filled = Column(Boolean, default=False)
    filled_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
