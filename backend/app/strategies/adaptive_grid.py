import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GridLevel:
    """Represents a grid level."""
    level: int
    price: float
    side: str  # "BUY" or "SELL"
    quantity: float
    is_filled: bool = False


class ATRCalculator:
    """Calculate Average True Range for volatility."""
    
    @staticmethod
    def calculate(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> float:
        """
        Calculate ATR using high, low, close prices.
        
        Args:
            high: High prices array
            low: Low prices array
            close: Close prices array
            period: ATR period (default 14)
            
        Returns:
            Current ATR value
        """
        tr = np.maximum(
            np.maximum(high - low, np.abs(high - np.roll(close, 1))),
            np.abs(low - np.roll(close, 1))
        )
        atr = pd.Series(tr).rolling(window=period).mean().iloc[-1]
        return float(atr) if not np.isnan(atr) else 0.0


class AdaptiveGridStrategy:
    """Adaptive Grid Trading Strategy."""
    
    def __init__(
        self,
        pair: str = "BTCUSDT",
        grid_levels: int = 10,
        grid_profit_per_trade: float = 0.1,  # 0.1%
        atr_period: int = 14,
        atr_multiplier: float = 2.0,
        reverse_mode: bool = False,
        initial_balance: float = 1000.0
    ):
        self.pair = pair
        self.grid_levels = grid_levels
        self.grid_profit_per_trade = grid_profit_per_trade
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.reverse_mode = reverse_mode
        self.initial_balance = initial_balance
        
        self.current_price: Optional[float] = None
        self.grid_levels_list: List[GridLevel] = []
        self.last_grid_center: Optional[float] = None
        
        logger.info(f"Initialized AdaptiveGridStrategy for {pair}")
    
    def update_price(self, price: float):
        """Update current market price."""
        self.current_price = price
    
    def calculate_atr_from_klines(self, klines: List[List]) -> float:
        """
        Calculate ATR from klines data.
        
        Args:
            klines: List of klines from exchange [open, high, low, close, volume, ...]
            
        Returns:
            ATR value
        """
        if len(klines) < self.atr_period:
            return 0.0
        
        # Extract OHLC from klines
        high = np.array([float(k[2]) for k in klines])  # index 2 = high
        low = np.array([float(k[3]) for k in klines])   # index 3 = low
        close = np.array([float(k[4]) for k in klines]) # index 4 = close
        
        return ATRCalculator.calculate(high, low, close, self.atr_period)
    
    def generate_grid(
        self, 
        center_price: float, 
        atr: float,
        quote_balance: float
    ) -> List[GridLevel]:
        """
        Generate adaptive grid levels.
        
        Args:
            center_price: Center price for grid
            atr: Average True Range (volatility)
            quote_balance: Available quote currency balance
            
        Returns:
            List of GridLevel objects
        """
        # Calculate grid step based on ATR
        grid_step = atr * self.atr_multiplier
        
        if grid_step == 0:
            # Fallback to percentage-based if ATR is 0
            grid_step = center_price * (self.grid_profit_per_trade / 100)
        
        # Calculate quantity per order based on available balance
        # Allocate equal portions to each grid level
        quantity_per_level = quote_balance / (self.grid_levels * center_price)
        
        self.grid_levels_list = []
        
        # Generate SELL levels (above center)
        for i in range(1, self.grid_levels // 2 + 1):
            price = center_price + (grid_step * i)
            level = GridLevel(
                level=i,
                price=price,
                side="SELL",
                quantity=quantity_per_level
            )
            self.grid_levels_list.append(level)
        
        # Generate BUY levels (below center)
        for i in range(1, self.grid_levels // 2 + 1):
            price = center_price - (grid_step * i)
            level = GridLevel(
                level=-i,
                price=price,
                side="BUY",
                quantity=quantity_per_level
            )
            self.grid_levels_list.append(level)
        
        self.last_grid_center = center_price
        
        logger.info(
            f"Generated grid with {len(self.grid_levels_list)} levels, "
            f"center={center_price}, atr={atr:.2f}, step={grid_step:.2f}"
        )
        
        return sorted(self.grid_levels_list, key=lambda x: x.price)
    
    def detect_grid_break(self) -> bool:
        """
        Detect if price has moved beyond grid boundaries.
        
        Returns:
            True if grid needs to be rebuilt
        """
        if not self.grid_levels_list or self.current_price is None:
            return False
        
        # Get grid boundaries
        min_price = min(gl.price for gl in self.grid_levels_list)
        max_price = max(gl.price for gl in self.grid_levels_list)
        
        # Check if price is outside boundaries
        if self.current_price < min_price or self.current_price > max_price:
            logger.warning(
                f"Grid break detected! Current price {self.current_price} "
                f"is outside [{min_price}, {max_price}]"
            )
            return True
        
        return False
    
    def get_next_orders(self) -> List[Tuple[str, float, float]]:
        """
        Get next orders to place based on grid.
        
        Returns:
            List of (side, price, quantity) tuples
        """
        if not self.current_price or not self.grid_levels_list:
            return []
        
        orders = []
        
        for level in self.grid_levels_list:
            if not level.is_filled:
                # Check if price is at this level
                if abs(level.price - self.current_price) / self.current_price < 0.001:  # 0.1% tolerance
                    orders.append((level.side, level.price, level.quantity))
        
        return orders
    
    def mark_level_filled(self, price: float):
        """Mark a grid level as filled when trade executes."""
        for level in self.grid_levels_list:
            if abs(level.price - price) / price < 0.01:  # 1% tolerance
                level.is_filled = True
                logger.info(f"Marked grid level {level.level} as filled at {price}")
                break
    
    def get_grid_status(self) -> Dict:
        """Get current grid status."""
        if not self.grid_levels_list:
            return {}
        
        filled = sum(1 for l in self.grid_levels_list if l.is_filled)
        
        return {
            "total_levels": len(self.grid_levels_list),
            "filled_levels": filled,
            "unfilled_levels": len(self.grid_levels_list) - filled,
            "center_price": self.last_grid_center,
            "current_price": self.current_price,
            "levels": [
                {
                    "level": l.level,
                    "price": l.price,
                    "side": l.side,
                    "is_filled": l.is_filled,
                    "quantity": l.quantity
                }
                for l in sorted(self.grid_levels_list, key=lambda x: x.price)
            ]
        }


class ReverseStrategy:
    """Reverse trend-following strategy (optional mode)."""
    
    def __init__(self, pair: str = "BTCUSDT"):
        self.pair = pair
        self.trend = None  # "UPTREND", "DOWNTREND", None
        self.entry_price: Optional[float] = None
    
    def detect_trend(self, prices: List[float], ema_period: int = 20) -> str:
        """
        Detect trend using EMA.
        
        Args:
            prices: List of recent prices
            ema_period: EMA period
            
        Returns:
            "UPTREND", "DOWNTREND", or None
        """
        if len(prices) < ema_period:
            return None
        
        ema = pd.Series(prices).ewm(span=ema_period).mean().iloc[-1]
        current_price = prices[-1]
        
        if current_price > ema:
            return "UPTREND"
        elif current_price < ema:
            return "DOWNTREND"
        
        return None
    
    def get_signal(self, trend: str) -> Optional[str]:
        """
        Get trading signal based on trend.
        
        Args:
            trend: Current trend
            
        Returns:
            "BUY", "SELL", or None
        """
        if trend == "DOWNTREND":
            return "BUY"  # Buy on downtrend
        elif trend == "UPTREND":
            return "SELL"  # Sell on uptrend
        
        return None
