from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import numpy as np

from app.models.models import Trade, TradeStatus, PortfolioSnapshot, Strategy
from app.core.logger import get_logger

logger = get_logger(__name__)


class AnalyticsEngine:
    """
    Calculates trading analytics and statistics.
    
    Provides static methods for computing various trading metrics including:
    - Profitability metrics (total profit, ROI, win rate)
    - Risk metrics (drawdown, Sharpe ratio)
    - Trade analysis (durations, averages)
    """
    
    @staticmethod
    def calculate_total_profit(trades: List[Trade]) -> float:
        """
        Calculate total profit from all closed trades.
        
        Args:
            trades: List of Trade objects
            
        Returns:
            Total profit in USDT
        """
        total = 0.0
        for trade in trades:
            if trade.status == TradeStatus.CLOSED:
                total += trade.profit_loss
        return total
    
    @staticmethod
    def calculate_roi(initial_balance: float, current_balance: float) -> float:
        """
        Calculate Return on Investment percentage.
        
        Args:
            initial_balance: Starting balance
            current_balance: Current balance
            
        Returns:
            ROI percentage
        """
        if initial_balance == 0:
            return 0.0
        return ((current_balance - initial_balance) / initial_balance) * 100
    
    @staticmethod
    def calculate_win_rate(trades: List[Trade]) -> float:
        """
        Calculate win rate (profitable trades / total trades).
        
        Args:
            trades: List of Trade objects
            
        Returns:
            Win rate percentage (0-100)
        """
        closed_trades = [t for t in trades if t.status == TradeStatus.CLOSED]
        
        if not closed_trades:
            return 0.0
        
        winning_trades = sum(1 for t in closed_trades if t.profit_loss > 0)
        return (winning_trades / len(closed_trades)) * 100
    
    @staticmethod
    def calculate_max_drawdown(portfolio_snapshots: List[PortfolioSnapshot]) -> float:
        """
        Calculate maximum drawdown from portfolio snapshots.
        
        Args:
            portfolio_snapshots: List of PortfolioSnapshot objects
            
        Returns:
            Max drawdown percentage
        """
        if not portfolio_snapshots:
            return 0.0
        
        max_value = portfolio_snapshots[0].total_value
        max_drawdown = 0.0
        
        for snapshot in portfolio_snapshots:
            if snapshot.total_value > max_value:
                max_value = snapshot.total_value
            
            drawdown = ((max_value - snapshot.total_value) / max_value) * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    @staticmethod
    def calculate_sharpe_ratio(
        returns: List[float],
        risk_free_rate: float = 0.0
    ) -> float:
        """
        Calculate Sharpe Ratio for strategy.
        
        Args:
            returns: List of returns (as decimals)
            risk_free_rate: Risk-free rate (default 0)
            
        Returns:
            Sharpe Ratio
        """
        import numpy as np
        
        if len(returns) < 2:
            return 0.0
        
        returns_arr = np.array(returns)
        excess_returns = returns_arr - risk_free_rate
        
        std_dev = np.std(excess_returns)
        if std_dev == 0 or np.isnan(std_dev):
            return 0.0
        
        mean_val = np.mean(excess_returns)
        result = (mean_val / std_dev) * np.sqrt(252)  # Annualized
        return result if not np.isnan(result) else 0.0
    
    @staticmethod
    def get_trade_metrics(db: Session, strategy_id: int) -> Dict:
        """
        Get comprehensive trade metrics for a strategy.
        
        Args:
            db: Database session
            strategy_id: Strategy ID to analyze
            
        Returns:
            Dictionary containing:
            - total_trades: Total number of trades
            - closed_trades: Number of closed trades
            - open_trades: Number of open trades
            - total_profit: Total P&L
            - win_rate: Percentage of profitable trades
            - avg_profit_per_trade: Average profit per closed trade
            - longest_trade_duration_hours: Longest trade duration
            - best_trade: Best trade profit
            - worst_trade: Worst trade loss
        """
        trades = db.query(Trade).filter(Trade.strategy_id == strategy_id).all()
        
        closed_trades = [t for t in trades if t.status == TradeStatus.CLOSED]
        open_trades = [t for t in trades if t.status == TradeStatus.OPEN]
        
        total_profit = AnalyticsEngine.calculate_total_profit(trades)
        win_rate = AnalyticsEngine.calculate_win_rate(trades)
        
        avg_profit_per_trade = 0.0
        if len(closed_trades) > 0:
            avg_profit_per_trade = total_profit / len(closed_trades) if len(closed_trades) > 0 else 0.0
        
        longest_trade_duration = None
        if closed_trades:
            durations = [
                (t.closed_at - t.opened_at).total_seconds() / 3600
                for t in closed_trades if t.closed_at
            ]
            if durations:
                longest_trade_duration = max(durations)
        
        return {
            "total_trades": len(trades),
            "open_trades": len(open_trades),
            "closed_trades": len(closed_trades),
            "total_profit": total_profit,
            "win_rate": win_rate,
            "avg_profit_per_trade": avg_profit_per_trade,
            "longest_trade_duration_hours": longest_trade_duration,
            "best_trade": max((t.profit_loss for t in closed_trades), default=0),
            "worst_trade": min((t.profit_loss for t in closed_trades), default=0)
        }


class PortfolioTracker:
    """Tracks portfolio value and generates snapshots."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def take_snapshot(
        self,
        strategy_id: int,
        btc_balance: float,
        usdt_balance: float,
        btc_price: float
    ) -> PortfolioSnapshot:
        """
        Create a portfolio snapshot.
        
        Args:
            strategy_id: Strategy ID
            btc_balance: BTC balance
            usdt_balance: USDT balance
            btc_price: Current BTC price in USDT
            
        Returns:
            PortfolioSnapshot object
        """
        # Calculate total value
        total_value = usdt_balance + (btc_balance * btc_price)
        
        # Get strategy for initial balance
        strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
        initial_balance = strategy.total_profit + 1000  # Estimate
        
        # Calculate ROI
        roi = AnalyticsEngine.calculate_roi(initial_balance, total_value)
        
        # Create snapshot
        snapshot = PortfolioSnapshot(
            strategy_id=strategy_id,
            total_value=total_value,
            btc_balance=btc_balance,
            usdt_balance=usdt_balance,
            total_profit=strategy.total_profit,
            roi=roi,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        
        logger.info(
            f"Portfolio snapshot created: {total_value:.2f} USDT, "
            f"BTC: {btc_balance:.6f}, USDT: {usdt_balance:.2f}"
        )
        
        return snapshot
    
    def get_portfolio_history(
        self,
        strategy_id: int,
        limit: int = 100
    ) -> List[PortfolioSnapshot]:
        """Get recent portfolio snapshots."""
        return self.db.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.strategy_id == strategy_id
        ).order_by(PortfolioSnapshot.timestamp.desc()).limit(limit).all()
    
    def get_portfolio_overview(
        self,
        strategy_id: int,
        btc_balance: float,
        usdt_balance: float,
        btc_price: float
    ) -> Dict:
        """Get current portfolio overview."""
        strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
        
        if not strategy:
            return {}
        
        total_value = usdt_balance + (btc_balance * btc_price)
        initial_balance = strategy.total_profit + 1000  # Estimate
        roi = AnalyticsEngine.calculate_roi(initial_balance, total_value)
        
        # Get max drawdown
        snapshots = self.get_portfolio_history(strategy_id, limit=500)
        max_drawdown = AnalyticsEngine.calculate_max_drawdown(snapshots)
        
        return {
            "total_value_usdt": total_value,
            "btc_balance": btc_balance,
            "usdt_balance": usdt_balance,
            "btc_price": btc_price,
            "total_profit": strategy.total_profit,
            "roi_percent": roi,
            "max_drawdown_percent": max_drawdown,
            "active_trades": len([t for t in strategy.trades if t.status == TradeStatus.OPEN]),
            "active_orders": len([o for o in strategy.orders if o.status in ['open', 'partially_filled']])
        }
