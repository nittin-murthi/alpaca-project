"""
Alpaca API Client Wrapper
"""
import logging
from typing import Dict, List, Optional, Union
import pandas as pd
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import APIError

from config.settings import config

logger = logging.getLogger(__name__)

class AlpacaClient:
    """Enhanced Alpaca API client with error handling and utilities"""
    
    def __init__(self):
        self.api = tradeapi.REST(
            config.alpaca.api_key,
            config.alpaca.secret_key,
            config.alpaca.base_url,
            api_version='v2'
        )
        self._validate_connection()
    
    def _validate_connection(self) -> bool:
        """Validate API connection"""
        try:
            account = self.api.get_account()
            logger.info(f"Connected to Alpaca. Account status: {account.status}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")
            return False
    
    def get_account(self) -> Dict:
        """Get account information"""
        try:
            account = self.api.get_account()
            return {
                'equity': float(account.equity),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value),
                'day_trade_count': account.day_trade_count,
                'status': account.status
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """Get all positions"""
        try:
            positions = self.api.list_positions()
            return [
                {
                    'symbol': pos.symbol,
                    'qty': float(pos.qty),
                    'market_value': float(pos.market_value),
                    'cost_basis': float(pos.cost_basis),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_plpc': float(pos.unrealized_plpc)
                }
                for pos in positions
            ]
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def get_orders(self, status: str = 'all') -> List[Dict]:
        """Get orders by status"""
        try:
            orders = self.api.list_orders(status=status, limit=100)
            return [
                {
                    'id': order.id,
                    'symbol': order.symbol,
                    'side': order.side,
                    'order_type': order.order_type,
                    'qty': float(order.qty),
                    'filled_qty': float(order.filled_qty or 0),
                    'status': order.status,
                    'submitted_at': order.submitted_at,
                    'filled_at': order.filled_at
                }
                for order in orders
            ]
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []
    
    def place_order(
        self,
        symbol: str,
        qty: Union[int, float],
        side: str,
        order_type: str = 'market',
        time_in_force: str = 'day',
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        trail_percent: Optional[float] = None
    ) -> Optional[Dict]:
        """Place a trading order"""
        try:
            if not config.trading.trading_enabled:
                logger.warning("Trading is disabled. Order not placed.")
                return None
            
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                stop_price=stop_price,
                trail_percent=trail_percent
            )
            
            logger.info(f"Order placed: {side} {qty} {symbol} at {order_type}")
            return {
                'id': order.id,
                'symbol': order.symbol,
                'side': order.side,
                'qty': float(order.qty),
                'status': order.status
            }
        except APIError as e:
            logger.error(f"API Error placing order: {e}")
            return None
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            self.api.cancel_order(order_id)
            logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    def get_bars(
        self,
        symbols: Union[str, List[str]],
        timeframe: str = '1Day',
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """Get historical bars data"""
        try:
            if isinstance(symbols, str):
                symbols = [symbols]
            
            if not start:
                start = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            bars = self.api.get_bars(
                symbols,
                timeframe,
                start=start,
                end=end,
                limit=limit
            ).df
            
            return bars
        except Exception as e:
            logger.error(f"Error getting bars: {e}")
            return pd.DataFrame()
    
    def get_latest_quote(self, symbol: str) -> Optional[Dict]:
        """Get latest quote for symbol"""
        try:
            quote = self.api.get_latest_quote(symbol)
            return {
                'symbol': symbol,
                'bid': float(quote.bid_price),
                'ask': float(quote.ask_price),
                'bid_size': quote.bid_size,
                'ask_size': quote.ask_size,
                'timestamp': quote.timestamp
            }
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return None
    
    def is_market_open(self) -> bool:
        """Check if market is open"""
        try:
            clock = self.api.get_clock()
            return clock.is_open
        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            return False
    
    def get_market_calendar(self, days: int = 30) -> List[Dict]:
        """Get market calendar"""
        try:
            end_date = datetime.now() + timedelta(days=days)
            calendar = self.api.get_calendar(
                start=datetime.now().strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d')
            )
            return [
                {
                    'date': day.date,
                    'open': day.open,
                    'close': day.close
                }
                for day in calendar
            ]
        except Exception as e:
            logger.error(f"Error getting calendar: {e}")
            return []