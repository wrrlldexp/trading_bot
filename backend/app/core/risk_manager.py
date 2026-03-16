from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.models.models import Strategy, Trade, TradeStatus
from app.core.logger import get_logger

logger = get_logger(__name__)


class RiskManager:
    """Manages trading risk and limits."""
    
    def __init__(
        self,
        db: Session,
        max_position_size: float = 50.0,  # % of portfolio
        max_drawdown: float = 20.0,  # %
        max_active_orders: int = 20,
        emergency_stop: bool = False
    ):
        self.db = db
        self.max_position_size = max_position_size
        self.max_drawdown = max_drawdown
        self.max_active_orders = max_active_orders
        self.emergency_stop = emergency_stop
    
    def check_position_size(
        self,
        strategy_id: int,
        proposed_quantity: float,
        current_price: float,
        portfolio_value: float
    ) -> bool:
        """
        Check if proposed order size exceeds risk limit.
        
        Args:
            strategy_id: Strategy ID
            proposed_quantity: Quantity to order
            current_price: Current market price
            portfolio_value: Total portfolio value in USDT
            
        Returns:
            True if position size is acceptable
        """
        position_value = proposed_quantity * current_price
        position_percentage = (position_value / portfolio_value) * 100
        
        if position_percentage > self.max_position_size:
            logger.warning(
                f"Position size {position_percentage:.2f}% exceeds limit {self.max_position_size}%"
            )
            return False
        
        return True
    
    def check_max_active_orders(self, strategy_id: int, current_active: int) -> bool:
        """
        Check if adding another order would exceed max orders limit.
        
        Args:
            strategy_id: Strategy ID
            current_active: Current number of active orders
            
        Returns:
            True if within limits
        """
        if current_active >= self.max_active_orders:
            logger.warning(
                f"Max active orders limit reached: {current_active}/{self.max_active_orders}"
            )
            return False
        
        return True
    
    def calculate_drawdown(
        self,
        strategy_id: int,
        current_portfolio_value: float,
        peak_portfolio_value: float
    ) -> float:
        """
        Calculate current drawdown percentage.
        
        Args:
            strategy_id: Strategy ID
            current_portfolio_value: Current total portfolio value
            peak_portfolio_value: Peak portfolio value achieved
            
        Returns:
            Drawdown percentage (0-100)
        """
        if peak_portfolio_value == 0:
            return 0.0
        
        drawdown = ((peak_portfolio_value - current_portfolio_value) / peak_portfolio_value) * 100
        return max(0.0, drawdown)
    
    def check_drawdown_limit(
        self,
        current_drawdown: float
    ) -> bool:
        """
        Check if current drawdown exceeds maximum allowed.
        
        Args:
            current_drawdown: Current drawdown percentage
            
        Returns:
            True if within limits
        """
        if current_drawdown > self.max_drawdown:
            logger.warning(
                f"Drawdown {current_drawdown:.2f}% exceeds limit {self.max_drawdown}%"
            )
            return False
        
        return True
    
    def can_trade(
        self,
        strategy_id: int,
        proposed_quantity: float,
        current_price: float,
        portfolio_value: float,
        current_active_orders: int,
        current_drawdown: float
    ) -> tuple[bool, str]:
        """
        Comprehensive check if trade can be executed.
        
        Args:
            strategy_id: Strategy ID
            proposed_quantity: Order quantity
            current_price: Current price
            portfolio_value: Total portfolio value
            current_active_orders: Number of active orders
            current_drawdown: Current drawdown %
            
        Returns:
            (can_trade: bool, reason: str)
        """
        if self.emergency_stop:
            return False, "Emergency stop is active"
        
        if not self.check_drawdown_limit(current_drawdown):
            return False, f"Drawdown limit exceeded: {current_drawdown:.2f}%"
        
        if not self.check_max_active_orders(strategy_id, current_active_orders):
            return False, f"Max active orders reached: {current_active_orders}"
        
        if not self.check_position_size(strategy_id, proposed_quantity, current_price, portfolio_value):
            return False, f"Position size exceeds limit"
        
        return True, "OK"
    
    def trigger_emergency_stop(self, strategy_id: int):
        """Trigger emergency stop for a strategy."""
        try:
            strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if strategy:
                strategy.is_active = False
                strategy.status = "stopped"
                self.emergency_stop = True
                self.db.commit()
                logger.warning(f"Emergency stop triggered for strategy {strategy_id}")
        except Exception as e:
            logger.error(f"Failed to trigger emergency stop: {e}")
            self.db.rollback()
    
    def get_risk_status(self, strategy_id: int) -> Dict:
        """Get current risk status."""
        return {
            "max_position_size": self.max_position_size,
            "max_drawdown": self.max_drawdown,
            "max_active_orders": self.max_active_orders,
            "emergency_stop": self.emergency_stop
        }
