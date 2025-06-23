"""
Simplified Configuration Management (Python 3.13 Compatible)
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class SimpleConfig:
    """Simplified configuration class"""
    
    def __init__(self):
        # Alpaca Configuration
        self.alpaca_api_key = os.getenv('ALPACA_API_KEY', 'PKMTOA2SN17QT455YBCI')
        self.alpaca_secret_key = os.getenv('ALPACA_SECRET_KEY', 'YOUR_SECRET_KEY_HERE')
        self.alpaca_base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets/v2')
        self.alpaca_data_url = os.getenv('ALPACA_DATA_URL', 'https://data.alpaca.markets/v2')
        
        # News Configuration
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        
        # Risk Management
        self.max_position_size = float(os.getenv('MAX_POSITION_SIZE', '0.02'))
        self.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS', '0.05'))
        self.stop_loss_percent = float(os.getenv('STOP_LOSS_PERCENT', '0.02'))
        self.take_profit_percent = float(os.getenv('TAKE_PROFIT_PERCENT', '0.04'))
        
        # Trading Configuration
        self.trading_enabled = os.getenv('TRADING_ENABLED', 'false').lower() == 'true'
        self.min_volume = int(os.getenv('MIN_VOLUME', '1000000'))
        self.portfolio_value = float(os.getenv('PORTFOLIO_VALUE', '100000'))
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Database
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///ai_hedge_fund.db')
    
    def validate(self) -> bool:
        """Validate configuration"""
        try:
            # Basic validation
            if not self.alpaca_api_key or self.alpaca_api_key == 'YOUR_API_KEY_HERE':
                print("⚠️  Warning: Using demo API key")
            
            if self.trading_enabled and self.alpaca_secret_key == 'YOUR_SECRET_KEY_HERE':
                print("❌ Error: Cannot enable trading without valid secret key")
                return False
            
            if self.max_position_size <= 0 or self.max_position_size > 1:
                print("❌ Error: Max position size must be between 0 and 1")
                return False
            
            if self.portfolio_value <= 0:
                print("❌ Error: Portfolio value must be positive")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation error: {e}")
            return False
    
    def get_alpaca_config(self) -> dict:
        """Get Alpaca configuration as dictionary"""
        return {
            'api_key': self.alpaca_api_key,
            'secret_key': self.alpaca_secret_key,
            'base_url': self.alpaca_base_url,
            'data_url': self.alpaca_data_url
        }
    
    def get_risk_config(self) -> dict:
        """Get risk management configuration as dictionary"""
        return {
            'max_position_size': self.max_position_size,
            'max_daily_loss': self.max_daily_loss,
            'stop_loss_percent': self.stop_loss_percent,
            'take_profit_percent': self.take_profit_percent
        }
    
    def get_trading_config(self) -> dict:
        """Get trading configuration as dictionary"""
        return {
            'trading_enabled': self.trading_enabled,
            'min_volume': self.min_volume,
            'portfolio_value': self.portfolio_value
        }
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"""
AI Hedge Fund Configuration:
==========================
Alpaca API Key: {self.alpaca_api_key[:8]}...
Trading Enabled: {self.trading_enabled}
Portfolio Value: ${self.portfolio_value:,.2f}
Max Position Size: {self.max_position_size*100:.1f}%
Max Daily Loss: {self.max_daily_loss*100:.1f}%
Stop Loss: {self.stop_loss_percent*100:.1f}%
Take Profit: {self.take_profit_percent*100:.1f}%
"""

# Create global config instance
config = SimpleConfig()