"""
Technical Analysis and Indicators Module
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import ta
import pandas_ta as ta_pandas
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Comprehensive technical analysis with multiple indicators"""
    
    def __init__(self):
        self.scaler = MinMaxScaler()
    
    def add_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add all technical indicators to dataframe"""
        if df.empty or len(df) < 20:
            return df
        
        try:
            # Ensure we have the required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_cols):
                logger.error("Missing required OHLCV columns")
                return df
            
            # Make a copy to avoid modifying original
            df = df.copy()
            
            # Price-based indicators
            df = self._add_moving_averages(df)
            df = self._add_bollinger_bands(df)
            df = self._add_rsi(df)
            df = self._add_macd(df)
            df = self._add_stochastic(df)
            df = self._add_adx(df)
            df = self._add_cci(df)
            df = self._add_williams_r(df)
            
            # Volume-based indicators
            df = self._add_volume_indicators(df)
            
            # Volatility indicators
            df = self._add_volatility_indicators(df)
            
            # Support/Resistance
            df = self._add_support_resistance(df)
            
            # Patterns
            df = self._add_candlestick_patterns(df)
            
            # Composite signals
            df = self._add_composite_signals(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error adding indicators: {e}")
            return df
    
    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add moving averages"""
        df['sma_5'] = ta.trend.sma_indicator(df['close'], window=5)
        df['sma_10'] = ta.trend.sma_indicator(df['close'], window=10)
        df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
        df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
        df['sma_200'] = ta.trend.sma_indicator(df['close'], window=200)
        
        df['ema_5'] = ta.trend.ema_indicator(df['close'], window=5)
        df['ema_10'] = ta.trend.ema_indicator(df['close'], window=10)
        df['ema_20'] = ta.trend.ema_indicator(df['close'], window=20)
        df['ema_50'] = ta.trend.ema_indicator(df['close'], window=50)
        
        # Moving average signals
        df['ma_signal_short'] = np.where(df['sma_5'] > df['sma_10'], 1, -1)
        df['ma_signal_long'] = np.where(df['sma_50'] > df['sma_200'], 1, -1)
        
        return df
    
    def _add_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Bollinger Bands"""
        bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = bb.bollinger_wband()
        df['bb_percent'] = bb.bollinger_pband()
        
        # Bollinger Band signals
        df['bb_signal'] = np.where(
            df['close'] > df['bb_upper'], 1,  # Overbought
            np.where(df['close'] < df['bb_lower'], -1, 0)  # Oversold
        )
        
        return df
    
    def _add_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add RSI indicator"""
        df['rsi'] = ta.momentum.rsi(df['close'], window=14)
        df['rsi_signal'] = np.where(
            df['rsi'] > 70, 1,  # Overbought
            np.where(df['rsi'] < 30, -1, 0)  # Oversold
        )
        return df
    
    def _add_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add MACD indicator"""
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histogram'] = macd.macd_diff()
        
        # MACD signals
        df['macd_buy_signal'] = np.where(
            (df['macd'] > df['macd_signal']) & 
            (df['macd'].shift(1) <= df['macd_signal'].shift(1)), 1, 0
        )
        df['macd_sell_signal'] = np.where(
            (df['macd'] < df['macd_signal']) & 
            (df['macd'].shift(1) >= df['macd_signal'].shift(1)), 1, 0
        )
        
        return df
    
    def _add_stochastic(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Stochastic Oscillator"""
        stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        
        df['stoch_signal'] = np.where(
            df['stoch_k'] > 80, 1,  # Overbought
            np.where(df['stoch_k'] < 20, -1, 0)  # Oversold
        )
        
        return df
    
    def _add_adx(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add ADX (Average Directional Index)"""
        df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
        df['adx_pos'] = ta.trend.adx_pos(df['high'], df['low'], df['close'], window=14)
        df['adx_neg'] = ta.trend.adx_neg(df['high'], df['low'], df['close'], window=14)
        
        # ADX signals (strong trend when ADX > 25)
        df['adx_signal'] = np.where(df['adx'] > 25, 1, 0)
        
        return df
    
    def _add_cci(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Commodity Channel Index"""
        df['cci'] = ta.trend.cci(df['high'], df['low'], df['close'], window=20)
        df['cci_signal'] = np.where(
            df['cci'] > 100, 1,  # Overbought
            np.where(df['cci'] < -100, -1, 0)  # Oversold
        )
        return df
    
    def _add_williams_r(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Williams %R"""
        df['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close'], lbp=14)
        df['williams_r_signal'] = np.where(
            df['williams_r'] > -20, 1,  # Overbought
            np.where(df['williams_r'] < -80, -1, 0)  # Oversold
        )
        return df
    
    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based indicators"""
        # On-Balance Volume
        df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])
        
        # Volume SMA
        df['volume_sma'] = ta.trend.sma_indicator(df['volume'], window=20)
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Accumulation/Distribution Line
        df['ad_line'] = ta.volume.acc_dist_index(df['high'], df['low'], df['close'], df['volume'])
        
        # Chaikin Money Flow
        df['cmf'] = ta.volume.chaikin_money_flow(df['high'], df['low'], df['close'], df['volume'])
        
        return df
    
    def _add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility indicators"""
        # Average True Range
        df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
        
        # Donchian Channels
        donchian = ta.volatility.DonchianChannel(df['high'], df['low'], df['close'])
        df['donchian_high'] = donchian.donchian_channel_hband()
        df['donchian_low'] = donchian.donchian_channel_lband()
        
        # Keltner Channels
        keltner = ta.volatility.KeltnerChannel(df['high'], df['low'], df['close'])
        df['keltner_high'] = keltner.keltner_channel_hband()
        df['keltner_low'] = keltner.keltner_channel_lband()
        
        return df
    
    def _add_support_resistance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add support and resistance levels"""
        # Simple pivot points
        df['pivot'] = (df['high'] + df['low'] + df['close']) / 3
        df['support1'] = 2 * df['pivot'] - df['high']
        df['resistance1'] = 2 * df['pivot'] - df['low']
        df['support2'] = df['pivot'] - (df['high'] - df['low'])
        df['resistance2'] = df['pivot'] + (df['high'] - df['low'])
        
        return df
    
    def _add_candlestick_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add candlestick pattern recognition"""
        # Doji pattern
        body = abs(df['close'] - df['open'])
        range_val = df['high'] - df['low']
        df['doji'] = np.where(body <= range_val * 0.1, 1, 0)
        
        # Hammer pattern
        lower_shadow = np.where(df['close'] > df['open'], 
                               df['open'] - df['low'], 
                               df['close'] - df['low'])
        upper_shadow = np.where(df['close'] > df['open'], 
                               df['high'] - df['close'], 
                               df['high'] - df['open'])
        
        df['hammer'] = np.where(
            (lower_shadow > body * 2) & (upper_shadow < body * 0.5), 1, 0
        )
        
        # Engulfing patterns
        df['bullish_engulfing'] = np.where(
            (df['close'].shift(1) < df['open'].shift(1)) &  # Previous was bearish
            (df['close'] > df['open']) &  # Current is bullish
            (df['open'] < df['close'].shift(1)) &  # Current open < previous close
            (df['close'] > df['open'].shift(1)), 1, 0  # Current close > previous open
        )
        
        df['bearish_engulfing'] = np.where(
            (df['close'].shift(1) > df['open'].shift(1)) &  # Previous was bullish
            (df['close'] < df['open']) &  # Current is bearish
            (df['open'] > df['close'].shift(1)) &  # Current open > previous close
            (df['close'] < df['open'].shift(1)), 1, 0  # Current close < previous open
        )
        
        return df
    
    def _add_composite_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add composite trading signals"""
        # Trend signals
        trend_signals = [
            'ma_signal_short', 'ma_signal_long', 'macd_buy_signal', 
            'macd_sell_signal', 'adx_signal'
        ]
        
        # Momentum signals
        momentum_signals = [
            'rsi_signal', 'stoch_signal', 'cci_signal', 'williams_r_signal'
        ]
        
        # Calculate composite scores
        df['trend_score'] = sum([df.get(signal, 0) for signal in trend_signals if signal in df.columns])
        df['momentum_score'] = sum([df.get(signal, 0) for signal in momentum_signals if signal in df.columns])
        
        # Overall signal
        df['composite_signal'] = (df['trend_score'] + df['momentum_score']) / 2
        
        # Buy/Sell signals
        df['buy_signal'] = np.where(df['composite_signal'] > 2, 1, 0)
        df['sell_signal'] = np.where(df['composite_signal'] < -2, 1, 0)
        
        return df
    
    def get_signal_strength(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate signal strength for latest data"""
        if df.empty:
            return {'strength': 0, 'direction': 'neutral'}
        
        latest = df.iloc[-1]
        
        # Collect all signals
        bullish_signals = 0
        bearish_signals = 0
        total_signals = 0
        
        signal_columns = [col for col in df.columns if 'signal' in col.lower()]
        
        for col in signal_columns:
            if col in latest:
                value = latest[col]
                if value > 0:
                    bullish_signals += 1
                elif value < 0:
                    bearish_signals += 1
                total_signals += 1
        
        if total_signals == 0:
            return {'strength': 0, 'direction': 'neutral'}
        
        net_bullish = (bullish_signals - bearish_signals) / total_signals
        
        return {
            'strength': abs(net_bullish),
            'direction': 'bullish' if net_bullish > 0 else 'bearish' if net_bullish < 0 else 'neutral',
            'bullish_signals': bullish_signals,
            'bearish_signals': bearish_signals,
            'total_signals': total_signals
        }