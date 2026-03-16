"""
API endpoints for grid management and adaptation.

Provides endpoints for:
- Управление переворотом ордеров
- Проверка адаптации сетки
- Перестройка сетки
- Статус сетки
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.core.database import get_db
from app.models.models import Strategy
from app.strategies.grid_flip_manager import GridFlipManager
from app.strategies.grid_adaptation import GridAdaptationManager
from app.core.logger import get_logger

router = APIRouter(prefix="/api/grid", tags=["grid-management"])
logger = get_logger(__name__)


@router.post("/strategies/{strategy_id}/flip-orders")
def flip_filled_orders(strategy_id: int, db: Session = Depends(get_db)) -> Dict:
    """
    Перевернуть все исполненные ордера стратегии на противоположные.
    
    Когда ордер заполнен (BUY исполнен), создается противоположный (SELL).
    
    Args:
        strategy_id: ID стратегии
        db: Database session
        
    Returns:
        Информация о перевёрнутых ордерах
    """
    
    # Проверить, существует ли стратегия
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Перевернуть ордера
    flipped_count = GridFlipManager.flip_filled_orders(strategy_id, db)
    
    return {
        "strategy_id": strategy_id,
        "flipped_orders": flipped_count,
        "status": "success"
    }


@router.post("/strategies/{strategy_id}/check-adaptation")
def check_grid_adaptation(
    strategy_id: int, 
    current_price: float,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Проверить нужна ли адаптация сетки.
    
    Проверяет крайние позиции. Если цена прошла за границы сетки,
    отмечает необходимость перестройки через 60 минут.
    
    Args:
        strategy_id: ID стратегии
        current_price: Текущая цена
        db: Database session
        
    Returns:
        Информация о необходимости адаптации
    """
    
    # Проверить, существует ли стратегия
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Проверить крайние позиции
    extreme_detected = GridAdaptationManager.check_extreme_positions(
        strategy_id, current_price, db
    )
    
    return {
        "strategy_id": strategy_id,
        "current_price": current_price,
        "extreme_position_detected": extreme_detected,
        "needs_rebuild": strategy.needs_rebuild
    }


@router.post("/strategies/{strategy_id}/rebuild-grid")
def rebuild_grid(
    strategy_id: int, 
    current_price: float,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Перестроить сетку ордеров по текущей цене.
    
    Отменяет все активные ордера и создает новую сетку.
    
    Args:
        strategy_id: ID стратегии
        current_price: Текущая цена для центра новой сетки
        db: Database session
        
    Returns:
        Информация о перестроенной сетке
    """
    
    # Проверить, существует ли стратегия
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Перестроить сетку
    created_orders = GridAdaptationManager.rebuild_grid(strategy_id, current_price, db)
    
    return {
        "strategy_id": strategy_id,
        "created_orders": created_orders,
        "center_price": current_price,
        "status": "success" if created_orders > 0 else "failed"
    }


@router.get("/strategies/{strategy_id}/status")
def get_grid_status(strategy_id: int, db: Session = Depends(get_db)) -> Dict:
    """
    Получить статус сетки и информацию об адаптации.
    
    Возвращает:
    - Количество активных ордеров
    - Диапазон цен сетки (min-max)
    - Статус адаптации и перестройки
    - Время до следующей перестройки
    
    Args:
        strategy_id: ID стратегии
        db: Database session
        
    Returns:
        Полная информация о статусе сетки
    """
    
    # Проверить, существует ли стратегия
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Получить статус
    grid_status = GridAdaptationManager.get_grid_status(strategy_id, db)
    
    return grid_status


@router.get("/strategies/{strategy_id}/should-rebuild")
def check_should_rebuild(strategy_id: int, db: Session = Depends(get_db)) -> Dict:
    """
    Проверить, пришло ли время для перестройки сетки.
    
    Возвращает True если:
    - Была обнаружена крайняя позиция
    - Прошло необходимое время (60 минут по умолчанию)
    
    Args:
        strategy_id: ID стратегии
        db: Database session
        
    Returns:
        Информация о необходимости перестройки
    """
    
    # Проверить, существует ли стратегия
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Проверить нужна ли перестройка
    should_rebuild = GridAdaptationManager.should_rebuild_grid(strategy_id, db)
    
    status = GridAdaptationManager.get_grid_status(strategy_id, db)
    
    return {
        "strategy_id": strategy_id,
        "should_rebuild": should_rebuild,
        "grid_status": status
    }
