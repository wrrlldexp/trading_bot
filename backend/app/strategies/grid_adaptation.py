"""
Grid Adaptation Manager - Управляет перестройкой сетки каждые 60 минут.

Когда крайний ордер из сетки исполнен (курс прошел за границы):
1. Система ждет 60 минут
2. Если курс вернулся в коридор → ничего не делаем
3. Если курс НЕ вернулся → перестраиваем сетку
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.models import Order, Strategy, OrderSide
from app.strategies.adaptive_grid import AdaptiveGridStrategy
from app.core.logger import get_logger

logger = get_logger(__name__)


class GridAdaptationManager:
    """Управляет адаптацией и перестройкой сетки ордеров."""
    
    @staticmethod
    def check_extreme_positions(strategy_id: int, current_price: float, db: Session) -> bool:
        """
        Проверяет крайние позиции сетки (верхний и нижний уровни).
        
        Если крайний ордер исполнен (цена прошла за его уровень):
        - Отмечает время обнаружения
        - Возвращает True если нужно ждать перестройку
        
        Args:
            strategy_id: ID стратегии
            current_price: Текущая цена
            db: Database session
            
        Returns:
            True если обнаружена крайняя позиция, требующая контроля
        """
        
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            logger.warning(f"Strategy {strategy_id} not found")
            return False
        
        # Получить все активные ордера сетки
        active_orders = db.query(Order).filter(
            Order.strategy_id == strategy_id,
            Order.status.in_(["open", "filled"]),
            Order.is_grid_order == True
        ).order_by(Order.price).all()
        
        if not active_orders:
            return False
        
        # Найти крайние уровни
        min_price = min(o.price for o in active_orders)
        max_price = max(o.price for o in active_orders)
        
        # Проверить, прошла ли цена за границы
        extreme_detected = False
        
        if current_price < min_price:
            logger.warning(f"Strategy {strategy_id}: Price {current_price} fell below grid min {min_price}")
            extreme_detected = True
        
        if current_price > max_price:
            logger.warning(f"Strategy {strategy_id}: Price {current_price} rose above grid max {max_price}")
            extreme_detected = True
        
        # Если крайняя позиция обнаружена → отметить время
        if extreme_detected:
            strategy.extreme_position_detected = datetime.utcnow()
            strategy.needs_rebuild = True
            db.commit()
            logger.info(f"Strategy {strategy_id}: Extreme position detected, will rebuild grid in {strategy.rebuild_interval_minutes} minutes")
            return True
        
        return False
    
    @staticmethod
    def should_rebuild_grid(strategy_id: int, db: Session) -> bool:
        """
        Проверяет, пришло ли время на перестройку сетки.
        
        Возвращает True если:
        - Крайняя позиция была обнаружена ранее
        - Прошло необходимое количество минут (по умолчанию 60)
        
        Args:
            strategy_id: ID стратегии
            db: Database session
            
        Returns:
            True если нужна перестройка сетки
        """
        
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy or not strategy.needs_rebuild:
            return False
        
        if not strategy.extreme_position_detected:
            return False
        
        # Проверить, прошло ли необходимое время
        elapsed = datetime.utcnow() - strategy.extreme_position_detected
        rebuild_time_seconds = strategy.rebuild_interval_minutes * 60
        
        if elapsed.total_seconds() >= rebuild_time_seconds:
            logger.info(f"Strategy {strategy_id}: Time to rebuild grid (elapsed: {elapsed.total_seconds()}s)")
            return True
        
        return False
    
    @staticmethod
    def rebuild_grid(strategy_id: int, current_price: float, db: Session) -> int:
        """
        Перестраивает сетку ордеров.
        
        Процесс:
        1. Отменить все активные ордера
        2. Получить параметры стратегии
        3. Создать новую сетку по текущей цене
        4. Обновить статус стратегии
        
        Args:
            strategy_id: ID стратегии
            current_price: Текущая цена для центра новой сетки
            db: Database session
            
        Returns:
            Количество созданных ордеров
        """
        
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            logger.warning(f"Strategy {strategy_id} not found for rebuild")
            return 0
        
        try:
            # 1. Отменить все активные ордера
            active_orders = db.query(Order).filter(
                Order.strategy_id == strategy_id,
                Order.status == "open",
                Order.is_grid_order == True
            ).all()
            
            cancelled_count = len(active_orders)
            for order in active_orders:
                order.status = "cancelled"
            
            db.commit()
            
            logger.info(f"Strategy {strategy_id}: Cancelled {cancelled_count} orders for rebuild")
            
            # 2. Создать новую сетку
            grid_strategy = AdaptiveGridStrategy(
                pair=strategy.pair,
                grid_levels=strategy.grid_levels,
                grid_profit_per_trade=strategy.grid_profit_per_trade,
                atr_period=strategy.atr_period,
                atr_multiplier=strategy.atr_multiplier,
                reverse_mode=strategy.reverse_mode
            )
            
            # Генерируем сетку
            grid_strategy.update_price(current_price)
            new_grid = grid_strategy.generate_grid(current_price)
            
            # 3. Создать новые ордера
            created_orders = 0
            
            for level in new_grid:
                try:
                    new_order = Order(
                        strategy_id=strategy_id,
                        pair=strategy.pair,
                        side=OrderSide.BUY if level.side == "BUY" else OrderSide.SELL,
                        price=level.price,
                        quantity=level.quantity,
                        status="open",
                        is_grid_order=True,
                        grid_level=level.level,
                        created_at=datetime.utcnow()
                    )
                    
                    db.add(new_order)
                    created_orders += 1
                    
                except Exception as e:
                    logger.error(f"Error creating order for level {level.level}: {str(e)}")
            
            # 4. Обновить статус стратегии
            strategy.needs_rebuild = False
            strategy.extreme_position_detected = None
            strategy.last_grid_rebuild = datetime.utcnow()
            
            db.commit()
            
            logger.info(
                f"Strategy {strategy_id}: Grid rebuilt successfully. "
                f"Cancelled: {cancelled_count}, Created: {created_orders}, "
                f"Center price: {current_price}"
            )
            
            return created_orders
            
        except Exception as e:
            logger.error(f"Error rebuilding grid for strategy {strategy_id}: {str(e)}")
            db.rollback()
            return 0
    
    @staticmethod
    def get_grid_status(strategy_id: int, db: Session) -> dict:
        """
        Получить статус сетки и информацию об адаптации.
        
        Args:
            strategy_id: ID стратегии
            db: Database session
            
        Returns:
            Словарь со статусом сетки
        """
        
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            return {"error": "Strategy not found"}
        
        # Получить количество активных ордеров
        active_orders = db.query(Order).filter(
            Order.strategy_id == strategy_id,
            Order.status == "open",
            Order.is_grid_order == True
        ).count()
        
        # Получить цены сетки
        all_orders = db.query(Order).filter(
            Order.strategy_id == strategy_id,
            Order.is_grid_order == True
        ).order_by(Order.price).all()
        
        # Информация об адаптации
        time_until_rebuild = None
        if strategy.extreme_position_detected and strategy.needs_rebuild:
            elapsed = datetime.utcnow() - strategy.extreme_position_detected
            remaining = (strategy.rebuild_interval_minutes * 60) - elapsed.total_seconds()
            time_until_rebuild = max(0, remaining)
        
        return {
            "strategy_id": strategy_id,
            "pair": strategy.pair,
            "grid_levels": strategy.grid_levels,
            "active_orders": active_orders,
            "total_orders": len(all_orders),
            "min_price": min((o.price for o in all_orders), default=None),
            "max_price": max((o.price for o in all_orders), default=None),
            "needs_rebuild": strategy.needs_rebuild,
            "extreme_position_detected": strategy.extreme_position_detected,
            "last_grid_rebuild": strategy.last_grid_rebuild,
            "time_until_rebuild_seconds": time_until_rebuild,
            "rebuild_interval_minutes": strategy.rebuild_interval_minutes
        }
