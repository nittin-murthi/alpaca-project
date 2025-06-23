"""
Simplified Trading Client using REST API calls
This replaces the problematic alpaca-trade-api for demonstration
"""
import requests
import logging
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf

from config.simple_settings import config

logger = logging.getLogger(__name__)

class SimpleTradingClient:
    """Simplified trading client using REST API calls"""
    
    def __init__(self):
        self.base_url = config.alpaca_base_url
        self.api_key = config.alpaca_api_key
        self.secret_key = config.alpaca_secret_key
        self.headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.secret_key,
            'Content-Type': 'application/json'
        }
        self.portfolio_value = float(config.portfolio_value)
        
    def get_account(self) -> Dict:
        """Get account information"""
        try:
            # For demo purposes, return simulated account data
            return {
                'id': 'demo_account',
                'account_number': '123456789',
                'status': 'ACTIVE',
                'currency': 'USD',
                'buying_power': str(self.portfolio_value),
                'regt_buying_power': str(self.portfolio_value),
                'cash': str(self.portfolio_value),
                'portfolio_value': str(self.portfolio_value),
                'equity': str(self.portfolio_value),
                'day_trade_count': 0,
                'pattern_day_trader': False
            }
        except Exception as e:
            logger.error(f"Error getting account: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        try:
            # For demo purposes, return empty positions
            return []
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def get_orders(self, status: str = 'all') -> List[Dict]:
        """Get orders"""
        try:
            # For demo purposes, return empty orders
            return []
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []
    
    def submit_order(self, symbol: str, qty: float, side: str, 
                    order_type: str = 'market', time_in_force: str = 'day',
                    limit_price: Optional[float] = None,
                    stop_price: Optional[float] = None) -> Dict:
        """Submit an order (simulated for demo)"""
        try:
            order_id = f"demo_order_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get current price for simulation
            ticker = yf.Ticker(symbol)
            current_price = ticker.history(period='1d')['Close'].iloc[-1]
            
            order = {
                'id': order_id,
                'client_order_id': order_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'submitted_at': datetime.now().isoformat(),
                'filled_at': None,
                'expired_at': None,
                'canceled_at': None,
                'failed_at': None,
                'replaced_at': None,
                'replaced_by': None,
                'replaces': None,
                'asset_id': symbol,
                'symbol': symbol,
                'asset_class': 'us_equity',
                'notional': None,
                'qty': str(qty),
                'filled_qty': '0',
                'filled_avg_price': None,
                'order_class': '',
                'order_type': order_type,
                'type': order_type,
                'side': side,
                'time_in_force': time_in_force,
                'limit_price': str(limit_price) if limit_price else None,
                'stop_price': str(stop_price) if stop_price else None,
                'status': 'accepted',
                'extended_hours': False,
                'legs': None,
                'trail_percent': None,
                'trail_price': None,
                'hwm': None
            }
            
            logger.info(f"Simulated order submitted: {side} {qty} {symbol} at ${current_price:.2f}")
            return order
            
        except Exception as e:
            logger.error(f"Error submitting order: {e}")
            return {}
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            logger.info(f"Simulated order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    def get_market_data(self, symbol: str, timeframe: str = '1Day', 
                       start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        """Get market data using yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Map timeframe to yfinance period
            period_map = {
                '1Min': '1d',
                '5Min': '5d', 
                '15Min': '1mo',
                '1Hour': '3mo',
                '1Day': '1y',
                '1Week': '2y',
                '1Month': '5y'
            }
            
            period = period_map.get(timeframe, '1y')
            
            if start and end:
                data = ticker.history(start=start, end=end, interval='1d')
            else:
                data = ticker.history(period=period, interval='1d')
                
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            
            # Rename columns to match Alpaca format
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_latest_quote(self, symbol: str) -> Dict:
        """Get latest quote"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            quote = {
                'symbol': symbol,
                'bid': info.get('bid', 0),
                'ask': info.get('ask', 0),
                'last': info.get('regularMarketPrice', 0),
                'volume': info.get('volume', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            return quote
            
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return {}
    
    def is_market_open(self) -> bool:
        """Check if market is open (simplified)"""
        now = datetime.now()
        # Simple check: weekdays 9:30 AM - 4:00 PM ET
        if now.weekday() >= 5:  # Weekend
            return False
        
        # Simplified time check (doesn't account for holidays)
        hour = now.hour
        return 9 <= hour < 16