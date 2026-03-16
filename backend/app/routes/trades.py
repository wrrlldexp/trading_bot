from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import Order, Trade, PortfolioSnapshot
from app.schemas.schemas import OrderResponse, TradeResponse, PortfolioSnapshot as PortfolioSnapshotSchema

router = APIRouter(prefix="/api", tags=["trades"])


@router.get("/orders", response_model=List[OrderResponse])
def get_orders(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get orders with optional filtering."""
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get specific order."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/trades", response_model=List[TradeResponse])
def get_trades(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get trades with optional filtering."""
    query = db.query(Trade)
    
    if status:
        query = query.filter(Trade.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/trades/{trade_id}", response_model=TradeResponse)
def get_trade(trade_id: int, db: Session = Depends(get_db)):
    """Get specific trade."""
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade


@router.get("/portfolio-history", response_model=List[PortfolioSnapshotSchema])
def get_portfolio_history(
    strategy_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get portfolio value history."""
    return db.query(PortfolioSnapshot).filter(
        PortfolioSnapshot.strategy_id == strategy_id
    ).order_by(PortfolioSnapshot.timestamp.desc()).offset(skip).limit(limit).all()
