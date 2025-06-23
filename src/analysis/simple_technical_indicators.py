"""
Simplified Technical Analysis Module (Python 3.13 Compatible)
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class SimpleTechnicalAnalyzer:
    """Simplified technical analysis with basic indicators"""
    
    def __init__(self):
        pass
    
    def add_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add all technical indicators to dataframe"""
        if df.empty or len(df) < 20:
            return df
        
        try:
            # Make a copy to avoid modifying original
            data = df.copy()
            
            # Ensure columns are lowercase
            data.columns = data.columns.str.lower()
            
            # Basic moving averages
            data = self._add_moving_averages(data)
            
            # RSI
            data = self._add_rsi(data)
            
            # MACD
            data = self._add_macd(data)
            
            # Bollinger Bands
            data = self._add_bollinger_bands(data)
            
            # Volume indicators
            data = self._add_volume_indicators(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error adding indicators: {e}")
            return df
    
    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add simple and exponential moving averages"""
        try:
            # Simple Moving Averages
            df['sma_5'] = df['close'].rolling(window=5).mean()
            df['sma_10'] = df['close'].rolling(window=10).mean()
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['sma_200'] = df['close'].rolling(window=200).mean()
            
            # Exponential Moving Averages
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            df['ema_50'] = df['close'].ewm(span=50).mean()
            
            return df
        except Exception as e:
            logger.error(f"Error adding moving averages: {e}")
            return df
    
    def _add_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add Relative Strength Index"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            return df
        except Exception as e:
            logger.error(f"Error adding RSI: {e}")
            return df
    
    def _add_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add MACD indicator"""
        try:
            # MACD Line
            df['macd'] = df['ema_12'] - df['ema_26']
            
            # Signal Line
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            
            # Histogram
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            return df
        except Exception as e:
            logger.error(f"Error adding MACD: {e}")
            return df
    
    def _add_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """Add Bollinger Bands"""
        try:
            # Middle Band (SMA)
            df['bb_middle'] = df['close'].rolling(window=period).mean()
            
            # Standard Deviation
            std = df['close'].rolling(window=period).std()
            
            # Upper and Lower Bands
            df['bb_upper'] = df['bb_middle'] + (std * std_dev)
            df['bb_lower'] = df['bb_middle'] - (std * std_dev)
            
            # Bollinger Band Width
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            
            # %B (Position within bands)
            df['bb_percent'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            return df
        except Exception as e:
            logger.error(f"Error adding Bollinger Bands: {e}")
            return df
    
    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based indicators"""
        try:
            # Volume Moving Average
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            
            # Volume Ratio
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # On-Balance Volume (OBV)
            df['obv'] = 0
            for i in range(1, len(df)):
                if df['close'].iloc[i] > df['close'].iloc[i-1]:
                    df['obv'].iloc[i] = df['obv'].iloc[i-1] + df['volume'].iloc[i]
                elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                    df['obv'].iloc[i] = df['obv'].iloc[i-1] - df['volume'].iloc[i]
                else:
                    df['obv'].iloc[i] = df['obv'].iloc[i-1]
            
            return df
        except Exception as e:
            logger.error(f"Error adding volume indicators: {e}")
            return df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on indicators"""
        try:
            # Initialize signals
            df['signal_rsi'] = 0
            df['signal_macd'] = 0
            df['signal_ma'] = 0
            df['signal_bb'] = 0
            df['signal_combined'] = 0
            
            # RSI Signals
            df.loc[df['rsi'] < 30, 'signal_rsi'] = 1  # Oversold - Buy
            df.loc[df['rsi'] > 70, 'signal_rsi'] = -1  # Overbought - Sell
            
            # MACD Signals
            df.loc[df['macd'] > df['macd_signal'], 'signal_macd'] = 1  # Bullish
            df.loc[df['macd'] < df['macd_signal'], 'signal_macd'] = -1  # Bearish
            
            # Moving Average Signals
            df.loc[df['sma_20'] > df['sma_50'], 'signal_ma'] = 1  # Bullish
            df.loc[df['sma_20'] < df['sma_50'], 'signal_ma'] = -1  # Bearish
            
            # Bollinger Band Signals
            df.loc[df['close'] < df['bb_lower'], 'signal_bb'] = 1  # Oversold
            df.loc[df['close'] > df['bb_upper'], 'signal_bb'] = -1  # Overbought
            
            # Combined Signal (simple average)
            df['signal_combined'] = (df['signal_rsi'] + df['signal_macd'] + 
                                   df['signal_ma'] + df['signal_bb']) / 4
            
            return df
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return df
    
    def get_latest_signals(self, df: pd.DataFrame) -> Dict[str, float]:
        """Get the latest trading signals"""
        try:
            if df.empty:
                return {}
            
            latest = df.iloc[-1]
            
            signals = {
                'rsi': latest.get('rsi', 0),
                'macd': latest.get('macd', 0),
                'macd_signal': latest.get('macd_signal', 0),
                'sma_20': latest.get('sma_20', 0),
                'sma_50': latest.get('sma_50', 0),
                'bb_upper': latest.get('bb_upper', 0),
                'bb_lower': latest.get('bb_lower', 0),
                'signal_rsi': latest.get('signal_rsi', 0),
                'signal_macd': latest.get('signal_macd', 0),
                'signal_ma': latest.get('signal_ma', 0),
                'signal_bb': latest.get('signal_bb', 0),
                'signal_combined': latest.get('signal_combined', 0),
                'close_price': latest.get('close', 0)
            }
            
            return signals
            
        except Exception as e:
            logger.error(f"Error getting latest signals: {e}")
            return {}
    
    def calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """Calculate overall trend strength"""
        try:
            if df.empty or len(df) < 50:
                return 0.0
            
            # Use last 20 periods for trend calculation
            recent_data = df.tail(20)
            
            # Calculate price momentum
            price_change = (recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]) / recent_data['close'].iloc[0]
            
            # Calculate volume trend
            volume_trend = recent_data['volume'].rolling(window=5).mean().iloc[-1] / recent_data['volume'].rolling(window=5).mean().iloc[0]
            
            # Combine metrics
            trend_strength = (price_change + (volume_trend - 1)) / 2
            
            return max(-1.0, min(1.0, trend_strength))  # Clamp between -1 and 1
            
        except Exception as e:
            logger.error(f"Error calculating trend strength: {e}")
            return 0.0