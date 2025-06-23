#!/usr/bin/env python3
"""
AI Hedge Fund - Main Application
Professional Trading System with Risk Management
"""
import os
import sys
import logging
import schedule
import time
from datetime import datetime
from typing import Dict, List
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.strategies.strategy_manager import StrategyManager
from config.settings import config
from loguru import logger as loguru_logger

class AIHedgeFund:
    """Main AI Hedge Fund Trading System"""
    
    def __init__(self):
        self.setup_logging()
        self.strategy_manager = StrategyManager()
        self.running = False
        
        # Validate configuration
        if not config.validate():
            raise ValueError("Configuration validation failed")
        
        logger.info("AI Hedge Fund initialized successfully")
        self.log_system_info()
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # Configure loguru
        loguru_logger.add(
            config.logging.log_file,
            rotation="10 MB",
            retention="30 days",
            level=config.logging.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
        )
        
        # Configure standard logging
        logging.basicConfig(
            level=getattr(logging, config.logging.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.logging.log_file),
                logging.StreamHandler()
            ]
        )
        
        # Set up logger
        global logger
        logger = logging.getLogger(__name__)
    
    def log_system_info(self):
        """Log system information and configuration"""
        logger.info("=" * 60)
        logger.info("AI HEDGE FUND TRADING SYSTEM")
        logger.info("=" * 60)
        logger.info(f"Trading Enabled: {config.trading.trading_enabled}")
        logger.info(f"Max Position Size: {config.risk.max_position_size:.1%}")
        logger.info(f"Max Daily Loss: {config.risk.max_daily_loss:.1%}")
        logger.info(f"Stop Loss: {config.risk.stop_loss_percent:.1%}")
        logger.info(f"Take Profit: {config.risk.take_profit_percent:.1%}")
        logger.info(f"Max Positions: {config.risk.max_positions}")
        logger.info(f"Trading Universe: {', '.join(config.trading.universe[:5])}...")
        logger.info("=" * 60)
    
    def run_trading_cycle(self):
        """Execute one complete trading cycle"""
        try:
            logger.info("Starting trading cycle...")
            cycle_start = datetime.now()
            
            # Step 1: Market Analysis
            logger.info("Phase 1: Market Analysis")
            market_analysis = self.strategy_manager.analyze_market()
            logger.info(f"Analyzed {market_analysis['symbols_analyzed']} symbols")
            
            # Step 2: Signal Generation
            logger.info("Phase 2: Signal Generation")
            signals = self.strategy_manager.generate_signals(market_analysis)
            logger.info(f"Generated {len(signals)} trading signals")
            
            # Log top signals
            for i, signal in enumerate(signals[:3], 1):
                logger.info(f"Top Signal #{i}: {signal.symbol} - {signal.action.upper()} "
                          f"(Confidence: {signal.confidence:.2f}) - {signal.reasoning}")
            
            # Step 3: Risk Check & Execution
            logger.info("Phase 3: Signal Execution")
            if signals:
                execution_results = self.strategy_manager.execute_signals(signals)
                logger.info(f"Executed {len(execution_results)} trades")
                
                for result in execution_results:
                    signal = result['signal']
                    logger.info(f"TRADE EXECUTED: {result['action']} {result['quantity']} "
                              f"{signal.symbol} (Confidence: {signal.confidence:.2f})")
            else:
                logger.info("No signals met execution criteria")
            
            # Step 4: Position Monitoring
            logger.info("Phase 4: Position Monitoring")
            position_status = self.strategy_manager.monitor_positions()
            
            # Log portfolio status
            logger.info(f"Portfolio Value: ${position_status['portfolio_value']:,.2f}")
            logger.info(f"Active Positions: {len(position_status['positions'])}")
            
            # Log risk alerts
            if position_status['alerts']:
                logger.warning("RISK ALERTS:")
                for alert in position_status['alerts']:
                    logger.warning(f"  - {alert}")
            
            # Emergency liquidation check
            if position_status['emergency_liquidation']:
                logger.critical("EMERGENCY LIQUIDATION REQUIRED!")
                self.emergency_liquidation()
            
            # Log exit recommendations
            if position_status['exit_recommendations']:
                logger.info("EXIT RECOMMENDATIONS:")
                for rec in position_status['exit_recommendations']:
                    logger.info(f"  - {rec['symbol']}: {rec['reason']} "
                              f"(PnL: {rec['unrealized_pnl_percent']:.2%})")
            
            # Save cycle data
            self.save_cycle_data({
                'timestamp': cycle_start,
                'market_analysis': market_analysis,
                'signals': [self._signal_to_dict(s) for s in signals],
                'execution_results': execution_results if 'execution_results' in locals() else [],
                'position_status': position_status
            })
            
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            logger.info(f"Trading cycle completed in {cycle_duration:.2f} seconds")
            logger.info("-" * 60)
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)
    
    def emergency_liquidation(self):
        """Emergency liquidation of all positions"""
        logger.critical("Executing emergency liquidation...")
        try:
            positions = self.strategy_manager._get_current_positions()
            
            for position in positions:
                logger.critical(f"Emergency selling {position.symbol}: {position.quantity} shares")
                
                order = self.strategy_manager.alpaca_client.place_order(
                    symbol=position.symbol,
                    qty=abs(position.quantity),
                    side='sell',
                    order_type='market'
                )
                
                if order:
                    logger.critical(f"Emergency sell order placed for {position.symbol}")
                else:
                    logger.error(f"Failed to place emergency sell order for {position.symbol}")
        
        except Exception as e:
            logger.error(f"Error in emergency liquidation: {e}")
    
    def save_cycle_data(self, data: Dict):
        """Save trading cycle data"""
        try:
            os.makedirs('data/cycles', exist_ok=True)
            timestamp = data['timestamp'].strftime('%Y%m%d_%H%M%S')
            filename = f'data/cycles/cycle_{timestamp}.json'
            
            # Convert datetime objects to strings for JSON serialization
            json_data = self._prepare_for_json(data)
            
            with open(filename, 'w') as f:
                json.dump(json_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving cycle data: {e}")
    
    def _signal_to_dict(self, signal) -> Dict:
        """Convert TradingSignal to dictionary"""
        return {
            'symbol': signal.symbol,
            'action': signal.action,
            'confidence': signal.confidence,
            'technical_score': signal.technical_score,
            'sentiment_score': signal.sentiment_score,
            'risk_score': signal.risk_score,
            'target_price': signal.target_price,
            'stop_loss': signal.stop_loss,
            'reasoning': signal.reasoning
        }
    
    def _prepare_for_json(self, obj):
        """Prepare object for JSON serialization"""
        if isinstance(obj, dict):
            return {k: self._prepare_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._prepare_for_json(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self._prepare_for_json(obj.__dict__)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj
    
    def start_scheduler(self):
        """Start the trading scheduler"""
        logger.info("Starting AI Hedge Fund scheduler...")
        
        # Schedule trading cycles
        if config.trading.trading_enabled:
            # Run every 30 minutes during market hours
            schedule.every(30).minutes.do(self.run_trading_cycle)
            logger.info("Scheduled trading cycles every 30 minutes")
        else:
            # Run every hour in simulation mode
            schedule.every().hour.do(self.run_trading_cycle)
            logger.info("Scheduled analysis cycles every hour (simulation mode)")
        
        # Schedule daily risk report
        schedule.every().day.at("16:30").do(self.generate_daily_report)
        
        self.running = True
        
        # Run initial cycle
        self.run_trading_cycle()
        
        # Main scheduler loop
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Shutdown requested...")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)
        
        logger.info("AI Hedge Fund stopped")
    
    def generate_daily_report(self):
        """Generate daily performance report"""
        try:
            logger.info("Generating daily report...")
            
            # Get portfolio status
            position_status = self.strategy_manager.monitor_positions()
            
            # Create report
            report = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'portfolio_value': position_status['portfolio_value'],
                'positions': position_status['positions'],
                'risk_metrics': position_status['risk_metrics'].__dict__,
                'alerts': position_status['alerts']
            }
            
            # Save report
            os.makedirs('reports', exist_ok=True)
            report_file = f"reports/daily_report_{datetime.now().strftime('%Y%m%d')}.json"
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Daily report saved: {report_file}")
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
    
    def stop(self):
        """Stop the trading system"""
        self.running = False

def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    AI HEDGE FUND SYSTEM                      ║
    ║                 Professional Trading Platform                ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🚨 IMPORTANT DISCLAIMERS:
    
    1. PAPER TRADING ONLY: This system uses Alpaca's paper trading API
    2. NO FINANCIAL ADVICE: This is educational software, not investment advice
    3. RISK WARNING: Trading involves substantial risk of loss
    4. REALISTIC EXPECTATIONS: 10% weekly returns are not realistic or sustainable
    5. PROPER TESTING: Thoroughly backtest before any live trading consideration
    
    Current Configuration:
    • Trading Enabled: {}
    • Max Position Size: {:.1%}
    • Max Daily Loss: {:.1%}
    • Universe Size: {} symbols
    
    """.format(
        config.trading.trading_enabled,
        config.risk.max_position_size,
        config.risk.max_daily_loss,
        len(config.trading.universe)
    ))
    
    if not config.trading.trading_enabled:
        print("🔍 SIMULATION MODE - No actual trades will be placed")
    else:
        print("⚠️  LIVE TRADING MODE - Real orders will be placed!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Exiting...")
            return
    
    try:
        # Initialize the AI Hedge Fund
        hedge_fund = AIHedgeFund()
        
        # Start the trading system
        hedge_fund.start_scheduler()
        
    except KeyboardInterrupt:
        print("\n\nShutdown requested by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True)
    finally:
        print("AI Hedge Fund system stopped")

if __name__ == "__main__":
    main()