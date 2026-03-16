import asyncio
import json
import websockets
from datetime import datetime
from typing import Callable, Optional

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class BinanceWebSocket:
    """Real-time WebSocket connection to Binance."""
    
    def __init__(self, pair: str = None):
        self.pair = (pair or settings.TRADING_PAIR).lower()
        self.is_connected = False
        self.ws = None
        self.handlers = {}
        
        # Testnet or mainnet
        if settings.BINANCE_TESTNET:
            self.base_url = "wss://stream.testnet.binance.vision:9443"
        else:
            self.base_url = "wss://stream.binance.com:9443"
    
    def subscribe_to_ticker(self, callback: Callable):
        """Subscribe to ticker updates (24h stats)."""
        self.handlers['ticker'] = callback
        return f"{self.pair}@ticker"
    
    def subscribe_to_price(self, callback: Callable):
        """Subscribe to price updates."""
        self.handlers['price'] = callback
        return f"{self.pair}@trade"
    
    def subscribe_to_kline(self, interval: str = "1h", callback: Callable = None):
        """Subscribe to candlestick data."""
        if callback:
            self.handlers['kline'] = callback
        return f"{self.pair}@kline_{interval}"
    
    def subscribe_to_orderbook(self, callback: Callable, depth: int = 10):
        """Subscribe to order book updates."""
        self.handlers['orderbook'] = callback
        return f"{self.pair}@depth{depth}@100ms"
    
    async def connect(self, stream_names: list):
        """Connect to WebSocket streams."""
        try:
            # Create stream URL
            streams = "/".join(stream_names)
            url = f"{self.base_url}/stream?streams={streams}"
            
            async with websockets.connect(url) as websocket:
                self.ws = websocket
                self.is_connected = True
                logger.info(f"Connected to WebSocket: {self.pair}")
                
                while self.is_connected:
                    try:
                        message = await asyncio.wait_for(
                            websocket.recv(), 
                            timeout=30.0
                        )
                        await self._handle_message(message)
                    except asyncio.TimeoutError:
                        logger.warning("WebSocket timeout, reconnecting...")
                        break
                    except Exception as e:
                        logger.error(f"Error receiving message: {e}")
                        break
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            self.is_connected = False
    
    async def _handle_message(self, message: str):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            stream = data.get('stream', '')
            event = data.get('data', {})
            
            # Route to appropriate handler
            if 'ticker' in stream and 'ticker' in self.handlers:
                await self.handlers['ticker'](event)
            elif 'trade' in stream and 'price' in self.handlers:
                await self.handlers['price'](event)
            elif 'kline' in stream and 'kline' in self.handlers:
                await self.handlers['kline'](event)
            elif 'depth' in stream and 'orderbook' in self.handlers:
                await self.handlers['orderbook'](event)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON message: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def disconnect(self):
        """Disconnect from WebSocket."""
        self.is_connected = False
        if self.ws:
            await self.ws.close()
        logger.info(f"Disconnected from WebSocket: {self.pair}")


class MarketDataStream:
    """High-level market data streaming."""
    
    def __init__(self, pair: str = None):
        self.pair = pair or settings.TRADING_PAIR
        self.websocket = BinanceWebSocket(self.pair)
        self.current_price: Optional[float] = None
        self.ticker_data: Optional[dict] = None
        self.orderbook_data: Optional[dict] = None
    
    async def start(self):
        """Start receiving market data."""
        streams = []
        
        # Price updates
        streams.append(self.websocket.subscribe_to_price(self._on_price_update))
        
        # Ticker (24h stats)
        streams.append(self.websocket.subscribe_to_ticker(self._on_ticker_update))
        
        # Kline (candlesticks)
        streams.append(self.websocket.subscribe_to_kline("1h", self._on_kline_update))
        
        # Order book
        streams.append(self.websocket.subscribe_to_orderbook(
            self._on_orderbook_update, 
            depth=20
        ))
        
        await self.websocket.connect(streams)
    
    async def _on_price_update(self, data: dict):
        """Handle price update."""
        self.current_price = float(data.get('p', 0))
        logger.debug(f"Price update: {self.pair} = {self.current_price}")
    
    async def _on_ticker_update(self, data: dict):
        """Handle ticker update."""
        self.ticker_data = data
        logger.debug(f"Ticker update: {self.pair}")
    
    async def _on_kline_update(self, data: dict):
        """Handle kline update."""
        kline = data.get('k', {})
        logger.debug(f"Kline update: {self.pair} {kline.get('t')}")
    
    async def _on_orderbook_update(self, data: dict):
        """Handle orderbook update."""
        self.orderbook_data = data
        logger.debug(f"Orderbook update: {self.pair}")
    
    async def stop(self):
        """Stop receiving market data."""
        await self.websocket.disconnect()
    
    def get_current_price(self) -> Optional[float]:
        """Get latest price."""
        return self.current_price
