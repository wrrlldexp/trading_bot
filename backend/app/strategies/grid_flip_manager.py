"""
Grid Order Flip Manager - Управляет переворотом исполненных ордеров.

Основная функция: когда ордер исполнен (filled), создается противоположный ордер:
- BUY → SELL
- SELL → BUY

На том же уровне цены в сетке.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.models import Order, OrderSide, Strategy
from app.core.logger import get_logger

logger = get_logger(__name__)


class GridFlipManager:
    """Управляет автоматическим переворотом исполненных ордеров в сетке."""
    
    @staticmethod
    def flip_filled_orders(strategy_id: int, db: Session) -> int:
        """
        Переворачивает все исполненные ордера стратегии на противоположные.
        
        Когда ордер на покупку исполнен → создается ордер на продажу на том же уровне.
        Когда ордер на продажу исполнен → создается ордер на покупку на том же уровне.
        
        Args:
            strategy_id: ID стратегии
            db: Database session
            
        Returns:
            Количество перевёрнутых ордеров
        """
        
        # Получить все исполненные ордера, которые еще не были перевёрнуты
        filled_orders = db.query(Order).filter(
            Order.strategy_id == strategy_id,
            Order.status == "filled",
            Order.is_grid_order == True
        ).all()
        
        flipped_count = 0
        
        for order in filled_orders:
            # Проверить, есть ли уже противоположный ордер на этом уровне
            opposite_side = OrderSide.SELL if order.side == OrderSide.BUY else OrderSide.BUY
            
            existing_opposite = db.query(Order).filter(
                Order.strategy_id == strategy_id,
                Order.side == opposite_side,
                Order.price == order.price,
                Order.grid_level == order.grid_level,
                Order.status == "open"
            ).first()
            
            # Если противоположного ордера еще нет → создаем его
            if not existing_opposite:
                try:
                    new_order = Order(
                        strategy_id=strategy_id,
                        pair=order.pair,
                        side=opposite_side,
                        price=order.price,
                        quantity=order.quantity,
                        status="open",
                        is_grid_order=True,
                        grid_level=order.grid_level,
                        created_at=datetime.utcnow()
                    )
                    
                    db.add(new_order)
                    db.commit()
                    
                    flipped_count += 1
                    
                    logger.info(
                        f"Strategy {strategy_id}: Flipped order {order.id} "
                        f"({order.side.value}→{opposite_side.value}) at price {order.price}"
                    )
                    
                except Exception as e:
                    logger.error(f"Error flipping order {order.id}: {str(e)}")
                    db.rollback()
        
        return flipped_count
    
    @staticmethod
    def flip_single_order(order_id: int, db: Session) -> Optional[Order]:
        """
        Переворачивает один конкретный исполненный ордер.
        
        Args:
            order_id: ID ордера для переворота
            db: Database session
            
        Returns:
            Новый созданный ордер или None если ошибка
        """
        
        # Получить исходный ордер
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            logger.warning(f"Order {order_id} not found")
            return None
        
        if order.status != "filled":
            logger.warning(f"Order {order_id} status is {order.status}, not 'filled'")
            return None
        
        try:
            # Определить противоположную сторону
            opposite_side = OrderSide.SELL if order.side == OrderSide.BUY else OrderSide.BUY
            
            # Создать новый ордер
            new_order = Order(
                strategy_id=order.strategy_id,
                pair=order.pair,
                side=opposite_side,
                price=order.price,
                quantity=order.quantity,
                status="open",
                is_grid_order=True,
                grid_level=order.grid_level,
                created_at=datetime.utcnow()
            )
            
            db.add(new_order)
            db.commit()
            db.refresh(new_order)
            
            logger.info(
                f"Flipped order {order_id}: {order.side.value}→{opposite_side.value} "
                f"Price: {order.price}, New order ID: {new_order.id}"
            )
            
            return new_order
            
        except Exception as e:
            logger.error(f"Error flipping order {order_id}: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def get_filled_orders_count(strategy_id: int, db: Session) -> int:
        """
        Получить количество исполненных ордеров стратегии.
        
        Args:
            strategy_id: ID стратегии
            db: Database session
            
        Returns:
            Количество исполненных ордеров
        """
        
        count = db.query(Order).filter(
            Order.strategy_id == strategy_id,
            Order.status == "filled",
            Order.is_grid_order == True
        ).count()
        
        return count
