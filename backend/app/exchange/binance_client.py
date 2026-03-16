import asyncio
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from typing import Optional, Dict, List

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class BinanceClient:
    """Binance exchange integration."""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key or settings.BINANCE_API_KEY
        self.api_secret = api_secret or settings.BINANCE_API_SECRET
        
        # Initialize Binance client
        if settings.BINANCE_TESTNET:
            self.client = Client(self.api_key, self.api_secret, testnet=True)
        else:
            self.client = Client(self.api_key, self.api_secret)
        
        self.pair = settings.TRADING_PAIR
    
    def get_account_balance(self) -> Dict:
        """Get account balances."""
        try:
            account = self.client.get_account()
            return account
        except BinanceAPIException as e:
            logger.error(f"Error getting account balance: {e}")
            raise
    
    def get_balance(self, asset: str = "USDT") -> float:
        """Get balance for specific asset."""
        try:
            account = self.get_account_balance()
            for balance in account['balances']:
                if balance['asset'] == asset:
                    return float(balance['free'])
            return 0.0
        except Exception as e:
            logger.error(f"Error getting {asset} balance: {e}")
            return 0.0
    
    def get_current_price(self, pair: str = None) -> float:
        """Get current price of trading pair."""
        pair = pair or self.pair
        try:
            ticker = self.client.get_symbol_ticker(symbol=pair)
            return float(ticker['price'])
        except BinanceAPIException as e:
            logger.error(f"Error getting price for {pair}: {e}")
            raise
    
    def get_klines(self, pair: str = None, interval: str = "1h", limit: int = 100) -> List[Dict]:
        """Get candlestick data (klines)."""
        pair = pair or self.pair
        try:
            klines = self.client.get_klines(symbol=pair, interval=interval, limit=limit)
            return klines
        except BinanceAPIException as e:
            logger.error(f"Error getting klines for {pair}: {e}")
            raise
    
    def get_order_book(self, pair: str = None, limit: int = 20) -> Dict:
        """Get order book."""
        pair = pair or self.pair
        try:
            orderbook = self.client.get_order_book(symbol=pair, limit=limit)
            return orderbook
        except BinanceAPIException as e:
            logger.error(f"Error getting order book for {pair}: {e}")
            raise
    
    def place_limit_order(
        self, 
        pair: str, 
        side: str, 
        quantity: float, 
        price: float
    ) -> Dict:
        """Place a limit order.
        
        Args:
            pair: Trading pair (e.g., "BTCUSDT")
            side: "BUY" or "SELL"
            quantity: Order quantity
            price: Order price
            
        Returns:
            Order response from exchange
        """
        try:
            order = self.client.order_limit(
                symbol=pair,
                side=Client.SIDE_BUY if side.upper() == "BUY" else Client.SIDE_SELL,
                quantity=quantity,
                price=price
            )
            logger.info(f"Order placed: {order}")
            return order
        except (BinanceAPIException, BinanceOrderException) as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    def cancel_order(self, pair: str, order_id) -> Dict:
        """Cancel an order."""
        try:
            # Handle both string and int order IDs
            order_id_int = int(order_id) if isinstance(order_id, str) else order_id
            result = self.client.cancel_order(symbol=pair, orderId=order_id_int)
            logger.info(f"Order cancelled: {order_id}")
            return result
        except BinanceAPIException as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            raise
    
    def get_order_status(self, pair: str, order_id) -> Dict:
        """Get order status."""
        try:
            # Handle both string and int order IDs
            order_id_int = int(order_id) if isinstance(order_id, str) else order_id
            order = self.client.get_order(symbol=pair, orderId=order_id_int)
            return order
        except BinanceAPIException as e:
            logger.error(f"Error getting order status {order_id}: {e}")
            raise
    
    def get_open_orders(self, pair: str = None) -> List[Dict]:
        """Get open orders."""
        pair = pair or self.pair
        try:
            orders = self.client.get_open_orders(symbol=pair)
            return orders
        except BinanceAPIException as e:
            logger.error(f"Error getting open orders: {e}")
            raise
    
    def get_all_orders(self, pair: str = None, limit: int = 500) -> List[Dict]:
        """Get all orders for a pair."""
        pair = pair or self.pair
        try:
            orders = self.client.get_all_orders(symbol=pair, limit=limit)
            return orders
        except BinanceAPIException as e:
            logger.error(f"Error getting all orders: {e}")
            raise
    
    def ping(self) -> bool:
        """Test connection."""
        try:
            self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False


class AsyncBinanceClient:
    """Async wrapper for Binance client for WebSocket operations."""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.client = BinanceClient(api_key, api_secret)
        self.loop = asyncio.get_event_loop()
    
    async def get_current_price(self, pair: str = None) -> float:
        """Get current price asynchronously."""
        return await self.loop.run_in_executor(
            None, 
            self.client.get_current_price, 
            pair
        )
    
    async def place_order(self, pair: str, side: str, quantity: float, price: float) -> Dict:
        """Place order asynchronously."""
        return await self.loop.run_in_executor(
            None,
            self.client.place_limit_order,
            pair,
            side,
            quantity,
            price
        )
    
    async def cancel_order(self, pair: str, order_id: int) -> Dict:
        """Cancel order asynchronously."""
        return await self.loop.run_in_executor(
            None,
            self.client.cancel_order,
            pair,
            order_id
        )
