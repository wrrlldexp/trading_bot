from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from app.models.models import Order as OrderModel, OrderSide
from app.core.logger import get_logger
from app.exchange.binance_client import BinanceClient

logger = get_logger(__name__)


class OrderManager:
    """Manages order lifecycle."""
    
    def __init__(self, db: Session, binance_client: BinanceClient, pair: str = "BTCUSDT"):
        self.db = db
        self.binance = binance_client
        self.pair = pair
    
    def create_order(
        self,
        strategy_id: int,
        side: str,
        price: float,
        quantity: float,
        grid_level: Optional[int] = None,
        is_grid_order: bool = True
    ) -> OrderModel:
        """Create and place order on exchange."""
        try:
            # Place order on Binance
            exchange_order = self.binance.place_limit_order(
                self.pair,
                side,
                quantity,
                price
            )
            
            # Save to database
            order = OrderModel(
                strategy_id=strategy_id,
                exchange_order_id=str(exchange_order['orderId']),
                pair=self.pair,
                side=OrderSide(side.lower()),
                price=price,
                quantity=quantity,
                status=exchange_order['status'].lower(),
                grid_level=grid_level,
                is_grid_order=is_grid_order
            )
            
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            
            logger.info(f"Order created: {order.id} - {side} {quantity} @ {price}")
            return order
        
        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            self.db.rollback()
            raise
    
    def update_order_status(self, order: OrderModel):
        """Update order status from exchange."""
        try:
            # exchange_order_id is stored as string, no conversion needed
            exchange_order = self.binance.get_order_status(self.pair, order.exchange_order_id)
            
            order.status = exchange_order['status'].lower()
            order.filled_quantity = float(exchange_order.get('executedQty', 0))
            
            # Calculate average fill price
            if order.filled_quantity > 0:
                order.average_fill_price = float(exchange_order.get('cummulativeQuoteAssetTransactedQty', 0)) / order.filled_quantity
            
            # Mark as filled if status is FILLED
            if exchange_order['status'] == 'FILLED':
                order.filled_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Order {order.id} status updated: {order.status}")
            
        except Exception as e:
            logger.error(f"Failed to update order status: {e}")
            self.db.rollback()
            raise
    
    def cancel_order(self, order: OrderModel) -> bool:
        """Cancel an order."""
        try:
            if order.status not in ['open', 'partially_filled']:
                logger.warning(f"Cannot cancel order {order.id} with status {order.status}")
                return False
            
            # exchange_order_id is stored as string, no conversion needed
            self.binance.cancel_order(self.pair, order.exchange_order_id)
            order.status = 'cancelled'
            self.db.commit()
            
            logger.info(f"Order {order.id} cancelled")
            return True
        
        except Exception as e:
            logger.error(f"Failed to cancel order: {e}")
            self.db.rollback()
            return False
    
    def get_open_orders(self, strategy_id: int) -> List[OrderModel]:
        """Get all open orders for a strategy."""
        return self.db.query(OrderModel).filter(
            OrderModel.strategy_id == strategy_id,
            OrderModel.status.in_(['open', 'partially_filled'])
        ).all()
    
    def get_active_orders_count(self, strategy_id: int) -> int:
        """Get count of active orders."""
        return self.db.query(OrderModel).filter(
            OrderModel.strategy_id == strategy_id,
            OrderModel.status.in_(['open', 'partially_filled'])
        ).count()
    
    def refresh_all_orders(self, strategy_id: int):
        """Refresh status of all active orders."""
        open_orders = self.get_open_orders(strategy_id)
        
        for order in open_orders:
            try:
                self.update_order_status(order)
            except Exception as e:
                logger.error(f"Failed to refresh order {order.id}: {e}")
    
    def get_order_by_exchange_id(self, exchange_order_id: str) -> Optional[OrderModel]:
        """Get order by exchange order ID."""
        return self.db.query(OrderModel).filter(
            OrderModel.exchange_order_id == exchange_order_id
        ).first()
