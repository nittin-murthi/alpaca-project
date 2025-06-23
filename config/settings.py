"""
Configuration management for AI Hedge Fund
"""
import os
from typing import Optional, List
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()

class AlpacaConfig(BaseSettings):
    """Alpaca API configuration"""
    api_key: str = Field(..., env="ALPACA_API_KEY")
    secret_key: str = Field(..., env="ALPACA_SECRET_KEY")
    base_url: str = Field("https://paper-api.alpaca.markets/v2", env="ALPACA_BASE_URL")
    data_url: str = Field("https://data.alpaca.markets/v2", env="ALPACA_DATA_URL")

class NewsConfig(BaseSettings):
    """News API configuration"""
    news_api_key: Optional[str] = Field(None, env="NEWS_API_KEY")
    alpha_vantage_key: Optional[str] = Field(None, env="ALPHA_VANTAGE_API_KEY")

class RiskConfig(BaseSettings):
    """Risk management configuration"""
    max_position_size: float = Field(0.02, env="MAX_POSITION_SIZE")
    max_daily_loss: float = Field(0.05, env="MAX_DAILY_LOSS")
    stop_loss_percent: float = Field(0.02, env="STOP_LOSS_PERCENT")
    take_profit_percent: float = Field(0.04, env="TAKE_PROFIT_PERCENT")
    max_positions: int = Field(10, env="MAX_POSITIONS")

class TradingConfig(BaseSettings):
    """Trading configuration"""
    trading_enabled: bool = Field(False, env="TRADING_ENABLED")
    min_volume: int = Field(1000000, env="MIN_VOLUME")
    min_price: float = Field(5.0, env="MIN_PRICE")
    max_price: float = Field(500.0, env="MAX_PRICE")
    universe: List[str] = Field(default_factory=lambda: [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX",
        "SPY", "QQQ", "IWM", "GLD", "SLV", "TLT", "VIX"
    ])

class DatabaseConfig(BaseSettings):
    """Database configuration"""
    database_url: str = Field("sqlite:///ai_hedge_fund.db", env="DATABASE_URL")
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")

class LoggingConfig(BaseSettings):
    """Logging configuration"""
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/ai_hedge_fund.log", env="LOG_FILE")

class BacktestConfig(BaseSettings):
    """Backtesting configuration"""
    start_date: str = Field("2023-01-01", env="BACKTEST_START_DATE")
    end_date: str = Field("2024-01-01", env="BACKTEST_END_DATE")
    initial_capital: float = Field(100000, env="INITIAL_CAPITAL")

class Config:
    """Main configuration class"""
    def __init__(self):
        self.alpaca = AlpacaConfig()
        self.news = NewsConfig()
        self.risk = RiskConfig()
        self.trading = TradingConfig()
        self.database = DatabaseConfig()
        self.logging = LoggingConfig()
        self.backtest = BacktestConfig()
    
    def validate(self) -> bool:
        """Validate configuration"""
        try:
            # Check required fields
            if not self.alpaca.api_key:
                raise ValueError("ALPACA_API_KEY is required")
            
            # Validate risk parameters
            if self.risk.max_position_size <= 0 or self.risk.max_position_size > 1:
                raise ValueError("MAX_POSITION_SIZE must be between 0 and 1")
            
            if self.risk.max_daily_loss <= 0 or self.risk.max_daily_loss > 1:
                raise ValueError("MAX_DAILY_LOSS must be between 0 and 1")
            
            return True
        except Exception as e:
            print(f"Configuration validation error: {e}")
            return False

# Global configuration instance
config = Config()