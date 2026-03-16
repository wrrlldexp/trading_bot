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
    """
    Get paginated list of orders with optional status filtering.
    
    Args:
        skip: Number of records to skip for pagination (default: 0)
        limit: Maximum number of records to return (default: 100)
        status: Optional filter by order status (open, filled, cancelled, failed)
        db: Database session dependency
        
    Returns:
        List of OrderResponse objects
    """
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Get a specific order by ID.
    
    Args:
        order_id: The ID of the order to retrieve
        db: Database session dependency
        
    Returns:
        OrderResponse object
        
    Raises:
        HTTPException(404): If order is not found
    """
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
    """
    Get paginated list of trades with optional status filtering.
    
    Args:
        skip: Number of records to skip for pagination (default: 0)
        limit: Maximum number of records to return (default: 100)
        status: Optional filter by trade status (pending, open, closed, cancelled)
        db: Database session dependency
        
    Returns:
        List of TradeResponse objects
    """
    query = db.query(Trade)
    
    if status:
        query = query.filter(Trade.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/trades/{trade_id}", response_model=TradeResponse)
def get_trade(trade_id: int, db: Session = Depends(get_db)):
    """
    Get a specific trade by ID.
    
    Args:
        trade_id: The ID of the trade to retrieve
        db: Database session dependency
        
    Returns:
        TradeResponse object
        
    Raises:
        HTTPException(404): If trade is not found
    """
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
