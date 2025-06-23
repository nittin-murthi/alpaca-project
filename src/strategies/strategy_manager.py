"""
Strategy Manager - Main Trading Logic
"""
import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
from datetime import datetime
from dataclasses import dataclass

from src.trading.alpaca_client import AlpacaClient
from src.analysis.news_analyzer import NewsAnalyzer
from src.analysis.technical_indicators import TechnicalAnalyzer
from src.risk_management.risk_manager import RiskManager, Position
from config.settings import config

logger = logging.getLogger(__name__)

@dataclass
class TradingSignal:
    """Trading signal data class"""
    symbol: str
    action: str  # 'buy', 'sell', 'hold'
    confidence: float  # 0-1
    technical_score: float
    sentiment_score: float
    risk_score: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    reasoning: str = ""

class StrategyManager:
    """Main strategy coordination and execution"""
    
    def __init__(self):
        self.alpaca_client = AlpacaClient()
        self.news_analyzer = NewsAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.risk_manager = RiskManager()
        
        # Strategy parameters
        self.min_confidence = 0.6  # Minimum confidence to trade
        self.symbols = config.trading.universe
        
    def analyze_market(self) -> Dict:
        """Comprehensive market analysis"""
        logger.info("Starting market analysis...")
        
        # Get market sentiment
        market_sentiment = self.news_analyzer.get_market_sentiment(self.symbols)
        
        # Analyze each symbol
        symbol_analyses = {}
        
        for symbol in self.symbols:
            try:
                analysis = self._analyze_symbol(symbol)
                if analysis:
                    symbol_analyses[symbol] = analysis
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
        
        return {
            'timestamp': datetime.now(),
            'market_sentiment': market_sentiment,
            'symbol_analyses': symbol_analyses,
            'symbols_analyzed': len(symbol_analyses)
        }
    
    def _analyze_symbol(self, symbol: str) -> Optional[Dict]:
        """Analyze individual symbol"""
        try:
            # Get price data
            price_data = self.alpaca_client.get_bars([symbol], limit=200)
            if price_data.empty:
                logger.warning(f"No price data for {symbol}")
                return None
            
            # Add technical indicators
            price_data = self.technical_analyzer.add_all_indicators(price_data)
            
            # Get technical signal strength
            tech_signal = self.technical_analyzer.get_signal_strength(price_data)
            
            # Get news sentiment
            sentiment = self.news_analyzer.get_symbol_sentiment(symbol)
            
            # Get current quote
            quote = self.alpaca_client.get_latest_quote(symbol)
            current_price = quote['ask'] if quote else price_data['close'].iloc[-1]
            
            # Calculate volatility
            returns = price_data['close'].pct_change().dropna()
            volatility = returns.std() * (252 ** 0.5)  # Annualized volatility
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'technical_analysis': tech_signal,
                'sentiment_analysis': sentiment,
                'volatility': volatility,
                'price_data': price_data.tail(5),  # Last 5 days
                'analysis_time': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error in symbol analysis for {symbol}: {e}")
            return None
    
    def generate_signals(self, market_analysis: Dict) -> List[TradingSignal]:
        """Generate trading signals from market analysis"""
        signals = []
        
        for symbol, analysis in market_analysis['symbol_analyses'].items():
            try:
                signal = self._generate_symbol_signal(symbol, analysis, market_analysis['market_sentiment'])
                if signal and signal.confidence >= self.min_confidence:
                    signals.append(signal)
            except Exception as e:
                logger.error(f"Error generating signal for {symbol}: {e}")
        
        # Sort by confidence
        signals.sort(key=lambda x: x.confidence, reverse=True)
        
        return signals
    
    def _generate_symbol_signal(self, symbol: str, analysis: Dict, market_sentiment: Dict) -> Optional[TradingSignal]:
        """Generate trading signal for specific symbol"""
        try:
            tech_analysis = analysis['technical_analysis']
            sentiment_analysis = analysis['sentiment_analysis']
            current_price = analysis['current_price']
            volatility = analysis['volatility']
            
            # Technical score (0-1)
            tech_score = (tech_analysis['strength'] + 1) / 2  # Convert from -1,1 to 0,1
            if tech_analysis['direction'] == 'bearish':
                tech_score = 1 - tech_score
            
            # Sentiment score (0-1)
            sentiment_score = (sentiment_analysis['sentiment_score'] + 1) / 2  # Convert from -1,1 to 0,1
            
            # Market sentiment adjustment
            market_adj = (market_sentiment['overall_sentiment'] + 1) / 2  # Convert from -1,1 to 0,1
            
            # Risk score (lower volatility = higher score)
            risk_score = max(0, 1 - volatility)  # Inverse relationship with volatility
            
            # Combined confidence
            confidence = (tech_score * 0.4 + sentiment_score * 0.3 + market_adj * 0.2 + risk_score * 0.1)
            
            # Determine action
            if confidence > 0.7 and tech_analysis['direction'] == 'bullish':
                action = 'buy'
                target_price = current_price * 1.04  # 4% target
                stop_loss = current_price * 0.98  # 2% stop loss
                reasoning = f"Strong bullish signals: Tech={tech_analysis['direction']}, Sentiment={sentiment_analysis['sentiment_score']:.2f}"
            elif confidence < 0.3 and tech_analysis['direction'] == 'bearish':
                action = 'sell'
                target_price = current_price * 0.96  # 4% target (for shorts)
                stop_loss = current_price * 1.02  # 2% stop loss (for shorts)
                reasoning = f"Strong bearish signals: Tech={tech_analysis['direction']}, Sentiment={sentiment_analysis['sentiment_score']:.2f}"
            else:
                action = 'hold'
                target_price = None
                stop_loss = None
                reasoning = f"Mixed signals or low confidence: {confidence:.2f}"
            
            return TradingSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                technical_score=tech_score,
                sentiment_score=sentiment_score,
                risk_score=risk_score,
                target_price=target_price,
                stop_loss=stop_loss,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None
    
    def execute_signals(self, signals: List[TradingSignal]) -> List[Dict]:
        """Execute trading signals"""
        if not config.trading.trading_enabled:
            logger.info("Trading disabled. Signals not executed.")
            return []
        
        results = []
        account_info = self.alpaca_client.get_account()
        current_positions = self._get_current_positions()
        portfolio_value = account_info.get('portfolio_value', 0)
        daily_pnl = sum(pos.unrealized_pnl for pos in current_positions)
        
        for signal in signals:
            try:
                if signal.action == 'buy':
                    result = self._execute_buy_signal(signal, current_positions, portfolio_value, daily_pnl)
                elif signal.action == 'sell':
                    result = self._execute_sell_signal(signal, current_positions)
                else:
                    continue  # Skip hold signals
                
                if result:
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"Error executing signal for {signal.symbol}: {e}")
        
        return results
    
    def _execute_buy_signal(self, signal: TradingSignal, positions: List[Position], portfolio_value: float, daily_pnl: float) -> Optional[Dict]:
        """Execute buy signal"""
        # Check if we should enter position
        should_enter, reason = self.risk_manager.should_enter_position(
            signal.symbol, positions, portfolio_value, daily_pnl
        )
        
        if not should_enter:
            logger.info(f"Buy signal for {signal.symbol} rejected: {reason}")
            return None
        
        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            signal.symbol, 
            signal.target_price or 0,
            portfolio_value,
            signal.risk_score,
            signal.confidence
        )
        
        if position_size <= 0:
            logger.info(f"Position size too small for {signal.symbol}")
            return None
        
        # Place order
        order = self.alpaca_client.place_order(
            symbol=signal.symbol,
            qty=position_size,
            side='buy',
            order_type='market'
        )
        
        if order:
            logger.info(f"Buy order placed for {signal.symbol}: {position_size} shares")
            return {
                'signal': signal,
                'order': order,
                'action': 'buy_executed',
                'quantity': position_size
            }
        
        return None
    
    def _execute_sell_signal(self, signal: TradingSignal, positions: List[Position]) -> Optional[Dict]:
        """Execute sell signal"""
        # Find existing position
        position = next((pos for pos in positions if pos.symbol == signal.symbol), None)
        
        if not position:
            logger.info(f"No position found for sell signal: {signal.symbol}")
            return None
        
        # Check if we should exit
        should_exit, reason = self.risk_manager.should_exit_position(position)
        
        if not should_exit and signal.confidence < 0.8:
            logger.info(f"Sell signal for {signal.symbol} not strong enough: {signal.confidence}")
            return None
        
        # Place sell order
        order = self.alpaca_client.place_order(
            symbol=signal.symbol,
            qty=abs(position.quantity),
            side='sell',
            order_type='market'
        )
        
        if order:
            logger.info(f"Sell order placed for {signal.symbol}: {position.quantity} shares")
            return {
                'signal': signal,
                'order': order,
                'action': 'sell_executed',
                'quantity': position.quantity
            }
        
        return None
    
    def _get_current_positions(self) -> List[Position]:
        """Get current positions as Position objects"""
        positions = []
        alpaca_positions = self.alpaca_client.get_positions()
        
        for pos in alpaca_positions:
            position = Position(
                symbol=pos['symbol'],
                quantity=pos['qty'],
                entry_price=pos['cost_basis'] / pos['qty'] if pos['qty'] != 0 else 0,
                current_price=pos['market_value'] / pos['qty'] if pos['qty'] != 0 else 0,
                market_value=pos['market_value'],
                unrealized_pnl=pos['unrealized_pl'],
                unrealized_pnl_percent=pos['unrealized_plpc'],
                entry_time=datetime.now()  # Simplified - would need to track actual entry time
            )
            
            # Set stop loss and take profit
            position.stop_loss = self.risk_manager.calculate_stop_loss(position.entry_price)
            position.take_profit = self.risk_manager.calculate_take_profit(position.entry_price)
            
            positions.append(position)
        
        return positions
    
    def monitor_positions(self) -> Dict:
        """Monitor existing positions for exit signals"""
        positions = self._get_current_positions()
        account_info = self.alpaca_client.get_account()
        portfolio_value = account_info.get('portfolio_value', 0)
        
        # Calculate risk metrics
        risk_metrics = self.risk_manager.calculate_portfolio_risk(positions, portfolio_value)
        
        # Check for risk alerts
        alerts = self.risk_manager.get_risk_alerts(risk_metrics)
        
        # Check for emergency liquidation
        emergency = self.risk_manager.emergency_liquidation_needed(risk_metrics)
        
        # Check individual positions for exit signals
        exit_recommendations = []
        for position in positions:
            should_exit, reason = self.risk_manager.should_exit_position(position)
            if should_exit:
                exit_recommendations.append({
                    'symbol': position.symbol,
                    'reason': reason,
                    'current_price': position.current_price,
                    'unrealized_pnl': position.unrealized_pnl,
                    'unrealized_pnl_percent': position.unrealized_pnl_percent
                })
        
        return {
            'timestamp': datetime.now(),
            'portfolio_value': portfolio_value,
            'positions': [
                {
                    'symbol': pos.symbol,
                    'quantity': pos.quantity,
                    'market_value': pos.market_value,
                    'unrealized_pnl': pos.unrealized_pnl,
                    'unrealized_pnl_percent': pos.unrealized_pnl_percent
                }
                for pos in positions
            ],
            'risk_metrics': risk_metrics,
            'alerts': alerts,
            'emergency_liquidation': emergency,
            'exit_recommendations': exit_recommendations
        }