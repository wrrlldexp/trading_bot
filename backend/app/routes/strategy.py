from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import Strategy, Order, Trade
from app.schemas.schemas import (
    StrategyCreate, StrategyResponse, StrategyControl, 
    OrderResponse, TradeResponse, PortfolioOverview, StrategyStats
)

router = APIRouter(prefix="/api", tags=["strategies"])


def get_strategy_or_404(strategy_id: int, db: Session) -> Strategy:
    """Utility function to get strategy or raise 404."""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


def get_strategy_counts(strategy_id: int, db: Session) -> dict:
    """Utility function to get active orders and trades counts."""
    active_orders = db.query(Order).filter(
        Order.strategy_id == strategy_id,
        Order.status.in_(['open', 'partially_filled'])
    ).count()
    
    active_trades = db.query(Trade).filter(
        Trade.strategy_id == strategy_id,
        Trade.status == "open"
    ).count()
    
    return {"active_orders": active_orders, "active_trades": active_trades}


@router.post("/strategies", response_model=StrategyResponse)
def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    """Create a new trading strategy."""
    # Check if strategy with same name already exists
    existing = db.query(Strategy).filter(Strategy.name == strategy.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Strategy with this name already exists")
    
    db_strategy = Strategy(
        name=strategy.name,
        pair=strategy.pair,
        grid_levels=strategy.grid_levels,
        grid_profit_per_trade=strategy.grid_profit_per_trade,
        atr_period=strategy.atr_period,
        atr_multiplier=strategy.atr_multiplier,
        reverse_mode=strategy.reverse_mode
    )
    
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    
    return db_strategy


@router.get("/strategies", response_model=List[StrategyResponse])
def list_strategies(db: Session = Depends(get_db)):
    """Get all strategies."""
    return db.query(Strategy).all()


@router.get("/strategies/{strategy_id}", response_model=StrategyResponse)
def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Get specific strategy."""
    return get_strategy_or_404(strategy_id, db)


@router.post("/strategies/{strategy_id}/control")
def control_strategy(
    strategy_id: int, 
    control: StrategyControl,
    db: Session = Depends(get_db)
):
    """Control strategy (start, stop, pause, resume)."""
    strategy = get_strategy_or_404(strategy_id, db)
    
    action = control.action.lower()
    
    if action == "start":
        strategy.is_active = True
        strategy.status = "running"
    elif action == "stop":
        strategy.is_active = False
        strategy.status = "stopped"
    elif action == "pause":
        strategy.status = "paused"
    elif action == "resume":
        if strategy.status == "paused":
            strategy.status = "running"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    db.commit()
    return {"status": "success", "action": action}


@router.get("/strategies/{strategy_id}/orders", response_model=List[OrderResponse])
def get_strategy_orders(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Get all orders for a strategy."""
    get_strategy_or_404(strategy_id, db)  # Validate strategy exists
    return db.query(Order).filter(Order.strategy_id == strategy_id).all()


@router.get("/strategies/{strategy_id}/trades", response_model=List[TradeResponse])
def get_strategy_trades(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Get all trades for a strategy."""
    get_strategy_or_404(strategy_id, db)  # Validate strategy exists
    return db.query(Trade).filter(Trade.strategy_id == strategy_id).all()


@router.get("/strategies/{strategy_id}/portfolio", response_model=PortfolioOverview)
def get_portfolio(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Get portfolio overview."""
    strategy = get_strategy_or_404(strategy_id, db)
    counts = get_strategy_counts(strategy_id, db)
    
    active_orders = counts["active_orders"]
    active_trades = counts["active_trades"]
    
    return PortfolioOverview(
        current_total_value=1000 + strategy.total_profit,  # placeholder
        btc_balance=0.0,  # will be fetched from exchange
        usdt_balance=1000 + strategy.total_profit,
        total_profit=strategy.total_profit,
        roi=strategy.roi,
        max_drawdown=0.0,
        active_trades=active_trades,
        active_orders=active_orders,
        total_trades=strategy.total_trades,
        win_rate=strategy.win_rate
    )


@router.get("/strategies/{strategy_id}/stats", response_model=StrategyStats)
def get_strategy_stats(
    strategy_id: int,
    db: Session = Depends(get_db)
):
    """Get strategy statistics."""
    strategy = get_strategy_or_404(strategy_id, db)
    counts = get_strategy_counts(strategy_id, db)
    
    active_orders = counts["active_orders"]
    active_trades = counts["active_trades"]
    
    return StrategyStats(
        total_trades=strategy.total_trades,
        total_profit=strategy.total_profit,
        win_rate=strategy.win_rate,
        roi=strategy.roi,
        active_orders=active_orders,
        active_trades=active_trades,
        max_drawdown=0.0,
        uptime_seconds=0
    )
