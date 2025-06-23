"""
Risk Management System
"""
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass

from config.settings import config

logger = logging.getLogger(__name__)

@dataclass
class Position:
    """Position data class"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    entry_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass
class RiskMetrics:
    """Risk metrics data class"""
    portfolio_value: float
    cash: float
    total_exposure: float
    max_position_size: float
    current_drawdown: float
    max_drawdown: float
    daily_pnl: float
    daily_pnl_percent: float
    var_95: float  # Value at Risk 95%
    sharpe_ratio: float
    beta: float

class RiskManager:
    """Comprehensive risk management system"""
    
    def __init__(self):
        self.max_position_size = config.risk.max_position_size
        self.max_daily_loss = config.risk.max_daily_loss
        self.stop_loss_percent = config.risk.stop_loss_percent
        self.take_profit_percent = config.risk.take_profit_percent
        self.max_positions = config.risk.max_positions
        
        # Track daily PnL
        self.daily_pnl_history = []
        self.portfolio_history = []
        
    def calculate_position_size(
        self, 
        symbol: str, 
        entry_price: float, 
        portfolio_value: float,
        volatility: float = None,
        signal_strength: float = 1.0
    ) -> int:
        """Calculate optimal position size based on risk parameters"""
        try:
            # Base position size (percentage of portfolio)
            base_size = portfolio_value * self.max_position_size
            
            # Adjust for signal strength (0.5 to 1.5 multiplier)
            signal_multiplier = max(0.5, min(1.5, signal_strength))
            adjusted_size = base_size * signal_multiplier
            
            # Adjust for volatility if provided
            if volatility:
                # Reduce position size for high volatility stocks
                volatility_adjustment = max(0.5, 1 - (volatility - 0.2))
                adjusted_size *= volatility_adjustment
            
            # Calculate number of shares
            shares = int(adjusted_size / entry_price)
            
            # Ensure minimum position if signal is strong
            if shares == 0 and signal_strength > 0.8:
                shares = 1
            
            logger.info(f"Position size for {symbol}: {shares} shares (${shares * entry_price:.2f})")
            return shares
            
        except Exception as e:
            logger.error(f"Error calculating position size for {symbol}: {e}")
            return 0
    
    def calculate_stop_loss(self, entry_price: float, position_type: str = 'long') -> float:
        """Calculate stop loss price"""
        if position_type.lower() == 'long':
            return entry_price * (1 - self.stop_loss_percent)
        else:  # short position
            return entry_price * (1 + self.stop_loss_percent)
    
    def calculate_take_profit(self, entry_price: float, position_type: str = 'long') -> float:
        """Calculate take profit price"""
        if position_type.lower() == 'long':
            return entry_price * (1 + self.take_profit_percent)
        else:  # short position
            return entry_price * (1 - self.take_profit_percent)
    
    def should_enter_position(
        self, 
        symbol: str, 
        current_positions: List[Position],
        portfolio_value: float,
        daily_pnl: float
    ) -> Tuple[bool, str]:
        """Determine if we should enter a new position"""
        try:
            # Check if already at max positions
            if len(current_positions) >= self.max_positions:
                return False, "Maximum positions reached"
            
            # Check if we already have this symbol
            if any(pos.symbol == symbol for pos in current_positions):
                return False, f"Already have position in {symbol}"
            
            # Check daily loss limit
            daily_loss_percent = abs(daily_pnl) / portfolio_value if portfolio_value > 0 else 0
            if daily_pnl < 0 and daily_loss_percent >= self.max_daily_loss:
                return False, "Daily loss limit reached"
            
            # Check portfolio concentration
            total_exposure = sum(abs(pos.market_value) for pos in current_positions)
            exposure_percent = total_exposure / portfolio_value if portfolio_value > 0 else 0
            
            if exposure_percent >= 0.95:  # 95% max exposure
                return False, "Portfolio too concentrated"
            
            return True, "Position entry approved"
            
        except Exception as e:
            logger.error(f"Error checking position entry for {symbol}: {e}")
            return False, f"Error: {e}"
    
    def should_exit_position(self, position: Position) -> Tuple[bool, str]:
        """Determine if we should exit a position"""
        try:
            # Check stop loss
            if position.stop_loss and position.current_price <= position.stop_loss:
                return True, "Stop loss triggered"
            
            # Check take profit
            if position.take_profit and position.current_price >= position.take_profit:
                return True, "Take profit triggered"
            
            # Check time-based exit (hold for max 30 days)
            days_held = (datetime.now() - position.entry_time).days
            if days_held >= 30:
                return True, "Maximum hold period reached"
            
            # Check large unrealized loss (emergency exit)
            if position.unrealized_pnl_percent <= -0.10:  # 10% loss
                return True, "Emergency exit - large loss"
            
            return False, "Hold position"
            
        except Exception as e:
            logger.error(f"Error checking position exit for {position.symbol}: {e}")
            return False, f"Error: {e}"
    
    def calculate_portfolio_risk(
        self, 
        positions: List[Position], 
        portfolio_value: float,
        benchmark_returns: pd.Series = None
    ) -> RiskMetrics:
        """Calculate comprehensive portfolio risk metrics"""
        try:
            # Basic metrics
            total_exposure = sum(abs(pos.market_value) for pos in positions)
            cash = portfolio_value - sum(pos.market_value for pos in positions)
            
            # Calculate daily PnL
            daily_pnl = sum(pos.unrealized_pnl for pos in positions)
            daily_pnl_percent = daily_pnl / portfolio_value if portfolio_value > 0 else 0
            
            # Update history
            self.daily_pnl_history.append(daily_pnl_percent)
            self.portfolio_history.append(portfolio_value)
            
            # Keep only last 252 days (1 year)
            if len(self.daily_pnl_history) > 252:
                self.daily_pnl_history = self.daily_pnl_history[-252:]
                self.portfolio_history = self.portfolio_history[-252:]
            
            # Calculate drawdown
            if len(self.portfolio_history) > 1:
                peak = max(self.portfolio_history)
                current_drawdown = (portfolio_value - peak) / peak
                max_drawdown = self._calculate_max_drawdown()
            else:
                current_drawdown = 0
                max_drawdown = 0
            
            # Calculate VaR (95% confidence)
            if len(self.daily_pnl_history) >= 30:
                var_95 = np.percentile(self.daily_pnl_history, 5) * portfolio_value
            else:
                var_95 = 0
            
            # Calculate Sharpe ratio
            if len(self.daily_pnl_history) >= 30:
                returns = np.array(self.daily_pnl_history)
                sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
            else:
                sharpe_ratio = 0
            
            # Calculate Beta (if benchmark provided)
            beta = 0
            if benchmark_returns is not None and len(self.daily_pnl_history) >= 30:
                portfolio_returns = np.array(self.daily_pnl_history[-len(benchmark_returns):])
                if len(portfolio_returns) == len(benchmark_returns):
                    covariance = np.cov(portfolio_returns, benchmark_returns)[0][1]
                    benchmark_variance = np.var(benchmark_returns)
                    beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
            
            # Find max position size
            max_position_size = max([abs(pos.market_value) for pos in positions], default=0)
            
            return RiskMetrics(
                portfolio_value=portfolio_value,
                cash=cash,
                total_exposure=total_exposure,
                max_position_size=max_position_size,
                current_drawdown=current_drawdown,
                max_drawdown=max_drawdown,
                daily_pnl=daily_pnl,
                daily_pnl_percent=daily_pnl_percent,
                var_95=var_95,
                sharpe_ratio=sharpe_ratio,
                beta=beta
            )
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {e}")
            return RiskMetrics(
                portfolio_value=portfolio_value,
                cash=0, total_exposure=0, max_position_size=0,
                current_drawdown=0, max_drawdown=0, daily_pnl=0,
                daily_pnl_percent=0, var_95=0, sharpe_ratio=0, beta=0
            )
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown from portfolio history"""
        if len(self.portfolio_history) < 2:
            return 0
        
        portfolio_values = np.array(self.portfolio_history)
        peak = np.maximum.accumulate(portfolio_values)
        drawdown = (portfolio_values - peak) / peak
        
        return np.min(drawdown)
    
    def get_risk_alerts(self, risk_metrics: RiskMetrics) -> List[str]:
        """Get risk alerts based on current metrics"""
        alerts = []
        
        # Daily loss alert
        if risk_metrics.daily_pnl_percent <= -self.max_daily_loss * 0.8:
            alerts.append(f"Daily loss approaching limit: {risk_metrics.daily_pnl_percent:.2%}")
        
        # Drawdown alert
        if risk_metrics.current_drawdown <= -0.15:  # 15% drawdown
            alerts.append(f"High drawdown: {risk_metrics.current_drawdown:.2%}")
        
        # Concentration alert
        exposure_percent = risk_metrics.total_exposure / risk_metrics.portfolio_value
        if exposure_percent >= 0.9:
            alerts.append(f"High portfolio concentration: {exposure_percent:.2%}")
        
        # VaR alert
        var_percent = abs(risk_metrics.var_95) / risk_metrics.portfolio_value
        if var_percent >= 0.1:  # 10% VaR
            alerts.append(f"High Value at Risk: {var_percent:.2%}")
        
        return alerts
    
    def emergency_liquidation_needed(self, risk_metrics: RiskMetrics) -> bool:
        """Check if emergency liquidation is needed"""
        # Emergency conditions
        conditions = [
            risk_metrics.daily_pnl_percent <= -self.max_daily_loss,  # Daily loss limit
            risk_metrics.current_drawdown <= -0.25,  # 25% drawdown
            abs(risk_metrics.var_95) / risk_metrics.portfolio_value >= 0.15  # 15% VaR
        ]
        
        return any(conditions)