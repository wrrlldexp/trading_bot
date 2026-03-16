"""Demo data for development and testing."""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import Strategy, Order, Trade, PortfolioSnapshot, OrderSide, TradeStatus
from app.core.logger import get_logger

logger = get_logger(__name__)


def create_demo_data(db: Session):
    """Create demo strategy with sample data."""
    
    # Check if demo data already exists
    existing = db.query(Strategy).filter(Strategy.name == "Demo BTC Grid Bot").first()
    if existing:
        logger.info("Demo data already exists")
        return
    
    try:
        # Create demo strategy
        strategy = Strategy(
            name="Demo BTC Grid Bot",
            pair="BTCUSDT",
            is_active=True,
            status="running",
            grid_levels=10,
            grid_profit_per_trade=0.1,
            atr_period=14,
            atr_multiplier=2.0,
            reverse_mode=False,
            max_position_size=50.0,
            max_drawdown=20.0,
            max_active_orders=20,
            total_trades=24,
            total_profit=125.50,
            win_rate=83.33,
            roi=12.55
        )
        db.add(strategy)
        db.commit()
        db.refresh(strategy)
        
        logger.info(f"Created demo strategy: {strategy.id}")
        
        # Create demo orders
        orders_data = [
            ("BUY", 43500.00, 0.01, "filled"),
            ("SELL", 43655.00, 0.01, "filled"),
            ("BUY", 43400.00, 0.01, "filled"),
            ("SELL", 43560.00, 0.01, "filled"),
            ("BUY", 43200.00, 0.01, "open"),
            ("SELL", 43800.00, 0.01, "open"),
        ]
        
        now = datetime.utcnow()
        for i, (side, price, qty, status) in enumerate(orders_data):
            order = Order(
                strategy_id=strategy.id,
                exchange_order_id=str(1000000 + i),
                pair="BTCUSDT",
                side=OrderSide(side.lower()),
                price=price,
                quantity=qty,
                status=status,
                filled_quantity=qty if status == "filled" else 0,
                average_fill_price=price if status == "filled" else 0,
                commission=0.0001,
                is_grid_order=True,
                grid_level=i % 5,
                created_at=now - timedelta(hours=i),
                filled_at=now - timedelta(hours=i) if status == "filled" else None
            )
            db.add(order)
        
        db.commit()
        logger.info("Created 6 demo orders")
        
        # Create demo trades
        trades_data = [
            (43500.00, 43655.00, 0.01, "buy", "closed", 1.55, 0.36),
            (43400.00, 43560.00, 0.01, "buy", "closed", 1.60, 0.37),
            (43300.00, 43450.00, 0.01, "buy", "closed", 1.50, 0.35),
            (43200.00, 43350.00, 0.01, "buy", "closed", 1.50, 0.35),
            (43100.00, 43250.00, 0.01, "buy", "closed", 1.50, 0.35),
            (42900.00, 43050.00, 0.01, "buy", "closed", 1.50, 0.35),
            (42800.00, 42900.00, 0.01, "buy", "closed", 1.00, 0.23),
            (42700.00, 42850.00, 0.01, "buy", "closed", 1.50, 0.35),
            (42500.00, 42650.00, 0.01, "buy", "closed", 1.50, 0.35),
            (42400.00, 42550.00, 0.01, "buy", "closed", 1.50, 0.35),
            (42200.00, 42350.00, 0.01, "buy", "closed", 1.50, 0.35),
            (42100.00, 42250.00, 0.01, "buy", "closed", 1.50, 0.35),
            (43000.00, 43150.00, 0.01, "buy", "closed", 1.50, 0.35),
            (43500.00, 43650.00, 0.01, "buy", "closed", 1.50, 0.35),
            (43800.00, 43950.00, 0.01, "buy", "closed", 1.50, 0.35),
            (44000.00, 44150.00, 0.01, "buy", "closed", 1.50, 0.35),
            (44200.00, 44350.00, 0.01, "buy", "closed", 1.50, 0.35),
            (44500.00, 44650.00, 0.01, "buy", "closed", 1.50, 0.35),
            (44800.00, 44950.00, 0.01, "buy", "closed", 1.50, 0.35),
            (45000.00, 45150.00, 0.01, "buy", "closed", 1.50, 0.35),
            (45200.00, 45320.00, 0.01, "buy", "closed", 1.20, 0.27),
        ]
        
        for i, (entry, exit_price, qty, side, status, pnl, roi) in enumerate(trades_data):
            trade = Trade(
                strategy_id=strategy.id,
                pair="BTCUSDT",
                entry_price=entry,
                exit_price=exit_price,
                quantity=qty,
                side=OrderSide(side),
                status=TradeStatus(status),
                profit_loss=pnl,
                roi=roi,
                opened_at=now - timedelta(hours=20-i),
                closed_at=now - timedelta(hours=19-i) if status == "closed" else None
            )
            db.add(trade)
        
        # Create one open trade
        open_trade = Trade(
            strategy_id=strategy.id,
            pair="BTCUSDT",
            entry_price=45400.00,
            exit_price=None,
            quantity=0.01,
            side=OrderSide("buy"),
            status=TradeStatus("open"),
            profit_loss=0.0,
            roi=0.0,
            opened_at=now - timedelta(hours=2),
            closed_at=None
        )
        db.add(open_trade)
        
        db.commit()
        logger.info("Created 22 demo trades")
        
        # Create portfolio snapshots
        for i in range(24):
            portfolio_value = 1000 + (125.50 * i / 24)
            snapshot = PortfolioSnapshot(
                strategy_id=strategy.id,
                total_value=portfolio_value,
                btc_balance=0.01,
                usdt_balance=portfolio_value - 435,
                total_profit=125.50 * i / 24,
                roi=(125.50 * i / 24) / 1000 * 100,
                timestamp=now - timedelta(hours=24-i)
            )
            db.add(snapshot)
        
        db.commit()
        logger.info("Created 24 portfolio snapshots")
        
        logger.info("✅ Demo data created successfully!")
        
    except Exception as e:
        logger.error(f"Error creating demo data: {e}")
        db.rollback()
        raise
