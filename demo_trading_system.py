#!/usr/bin/env python3
"""
AI Hedge Fund Demo Script
This script demonstrates the core functionality of our trading system
"""
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import our modules
from src.analysis.simple_news_analyzer import SimpleNewsAnalyzer
from src.analysis.simple_technical_indicators import SimpleTechnicalAnalyzer
from src.trading.simple_trading_client import SimpleTradingClient
from config.simple_settings import config

def demonstrate_news_analysis():
    """Demonstrate news analysis functionality"""
    print("\n" + "="*60)
    print("🗞️  NEWS ANALYSIS DEMONSTRATION")
    print("="*60)
    
    try:
        news_analyzer = SimpleNewsAnalyzer()
        
        # Test symbols
        symbols = ['AAPL', 'TSLA', 'MSFT']
        
        for symbol in symbols:
            print(f"\n📈 Analyzing news sentiment for {symbol}...")
            
            # Get news sentiment (this would normally fetch real news)
            sentiment_score = news_analyzer.get_sentiment_score(symbol)
            
            if sentiment_score is not None:
                if sentiment_score > 0.1:
                    sentiment_text = "🟢 POSITIVE"
                elif sentiment_score < -0.1:
                    sentiment_text = "🔴 NEGATIVE"
                else:
                    sentiment_text = "🟡 NEUTRAL"
                
                print(f"   Sentiment Score: {sentiment_score:.3f} ({sentiment_text})")
            else:
                print(f"   Could not analyze sentiment for {symbol}")
                
    except Exception as e:
        print(f"❌ Error in news analysis: {e}")

def demonstrate_technical_analysis():
    """Demonstrate technical analysis functionality"""
    print("\n" + "="*60)
    print("📊 TECHNICAL ANALYSIS DEMONSTRATION")
    print("="*60)
    
    try:
        tech_analyzer = SimpleTechnicalAnalyzer()
        trading_client = SimpleTradingClient()
        
        # Test with AAPL
        symbol = 'AAPL'
        print(f"\n📈 Analyzing technical indicators for {symbol}...")
        
        # Get market data
        data = trading_client.get_market_data(symbol, timeframe='1Day')
        
        if data.empty:
            print(f"❌ Could not get market data for {symbol}")
            return
        
        print(f"   ✅ Retrieved {len(data)} days of market data")
        print(f"   📅 Latest close price: ${data['close'].iloc[-1]:.2f}")
        
        # Add technical indicators
        data_with_indicators = tech_analyzer.add_all_indicators(data)
        
        if not data_with_indicators.empty:
            latest = data_with_indicators.iloc[-1]
            
            print(f"\n🔍 Latest Technical Indicators:")
            
            # RSI
            if 'rsi' in latest and not pd.isna(latest['rsi']):
                rsi = latest['rsi']
                if rsi > 70:
                    rsi_signal = "🔴 OVERBOUGHT"
                elif rsi < 30:
                    rsi_signal = "🟢 OVERSOLD"
                else:
                    rsi_signal = "🟡 NEUTRAL"
                print(f"   RSI: {rsi:.2f} ({rsi_signal})")
            
            # MACD
            if 'macd' in latest and not pd.isna(latest['macd']):
                macd = latest['macd']
                macd_signal = latest.get('macd_signal', 0)
                if macd > macd_signal:
                    macd_trend = "🟢 BULLISH"
                else:
                    macd_trend = "🔴 BEARISH"
                print(f"   MACD: {macd:.4f} ({macd_trend})")
            
            # Moving Averages
            if 'sma_20' in latest and 'sma_50' in latest:
                sma_20 = latest['sma_20']
                sma_50 = latest['sma_50']
                if not pd.isna(sma_20) and not pd.isna(sma_50):
                    if sma_20 > sma_50:
                        ma_trend = "🟢 BULLISH"
                    else:
                        ma_trend = "🔴 BEARISH"
                    print(f"   SMA20: ${sma_20:.2f}, SMA50: ${sma_50:.2f} ({ma_trend})")
        
    except Exception as e:
        print(f"❌ Error in technical analysis: {e}")

def demonstrate_trading_simulation():
    """Demonstrate trading functionality"""
    print("\n" + "="*60)
    print("💰 TRADING SIMULATION DEMONSTRATION")
    print("="*60)
    
    try:
        trading_client = SimpleTradingClient()
        
        print("\n🏦 Getting account information...")
        account = trading_client.get_account()
        
        if account:
            print(f"   Account ID: {account['id']}")
            print(f"   Status: {account['status']}")
            print(f"   Portfolio Value: ${float(account['portfolio_value']):,.2f}")
            print(f"   Buying Power: ${float(account['buying_power']):,.2f}")
        
        print(f"\n📈 Checking current positions...")
        positions = trading_client.get_positions()
        if positions:
            for position in positions:
                print(f"   {position['symbol']}: {position['qty']} shares")
        else:
            print("   No current positions")
        
        print(f"\n💹 Market Status:")
        market_open = trading_client.is_market_open()
        print(f"   Market Open: {'🟢 YES' if market_open else '🔴 NO'}")
        
        # Simulate placing an order
        print(f"\n📋 Simulating order placement...")
        test_symbol = 'AAPL'
        quote = trading_client.get_latest_quote(test_symbol)
        
        if quote and quote.get('last', 0) > 0:
            current_price = quote['last']
            print(f"   Current {test_symbol} price: ${current_price:.2f}")
            
            # Calculate position size (1% of portfolio)
            portfolio_value = float(account['portfolio_value'])
            position_value = portfolio_value * 0.01
            shares = int(position_value / current_price)
            
            if shares > 0:
                print(f"   Calculated position size: {shares} shares (${position_value:.2f})")
                
                # Simulate buy order
                order = trading_client.submit_order(
                    symbol=test_symbol,
                    qty=shares,
                    side='buy',
                    order_type='market'
                )
                
                if order:
                    print(f"   ✅ Order submitted: {order['id']}")
                    print(f"      Action: {order['side'].upper()} {order['qty']} {order['symbol']}")
                    print(f"      Status: {order['status'].upper()}")
        
    except Exception as e:
        print(f"❌ Error in trading simulation: {e}")

def demonstrate_risk_management():
    """Demonstrate risk management calculations"""
    print("\n" + "="*60)
    print("⚠️  RISK MANAGEMENT DEMONSTRATION")
    print("="*60)
    
    try:
        print(f"\n🛡️  Risk Management Settings:")
        print(f"   Max Position Size: {config.max_position_size*100:.1f}% of portfolio")
        print(f"   Max Daily Loss: {config.max_daily_loss*100:.1f}% of portfolio")
        print(f"   Stop Loss: {config.stop_loss_percent*100:.1f}%")
        print(f"   Take Profit: {config.take_profit_percent*100:.1f}%")
        
        # Example calculations
        portfolio_value = 100000
        position_value = portfolio_value * config.max_position_size
        
        print(f"\n📊 Example Portfolio: ${portfolio_value:,.2f}")
        print(f"   Max Position Value: ${position_value:,.2f}")
        print(f"   Max Daily Loss: ${portfolio_value * config.max_daily_loss:,.2f}")
        
        # Example for AAPL
        example_price = 150.00
        shares = int(position_value / example_price)
        stop_loss_price = example_price * (1 - config.stop_loss_percent)
        take_profit_price = example_price * (1 + config.take_profit_percent)
        
        print(f"\n💼 Example Position (AAPL @ ${example_price:.2f}):")
        print(f"   Shares: {shares}")
        print(f"   Position Value: ${shares * example_price:,.2f}")
        print(f"   Stop Loss: ${stop_loss_price:.2f}")
        print(f"   Take Profit: ${take_profit_price:.2f}")
        print(f"   Risk per Share: ${example_price - stop_loss_price:.2f}")
        print(f"   Reward per Share: ${take_profit_price - example_price:.2f}")
        print(f"   Risk/Reward Ratio: 1:{(take_profit_price - example_price)/(example_price - stop_loss_price):.1f}")
        
    except Exception as e:
        print(f"❌ Error in risk management demo: {e}")

def main():
    """Main demo function"""
    print("🚀 AI HEDGE FUND SYSTEM DEMONSTRATION")
    print("=====================================")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version.split()[0]}")
    print(f"📁 Working Directory: {os.getcwd()}")
    
    # Demonstrate each component
    demonstrate_news_analysis()
    demonstrate_technical_analysis()
    demonstrate_trading_simulation()
    demonstrate_risk_management()
    
    print("\n" + "="*60)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*60)
    print("\n🔔 IMPORTANT REMINDERS:")
    print("• This is a DEMONSTRATION system using simulated trades")
    print("• Set TRADING_ENABLED=true in .env for live trading (EXTREMELY RISKY)")
    print("• Always test thoroughly before any live trading")
    print("• Never risk more than you can afford to lose")
    print("• 10% weekly returns are NOT realistic expectations")
    print("\n💡 Next Steps:")
    print("• Get real API keys for news services")
    print("• Implement proper backtesting")
    print("• Add more sophisticated risk management")
    print("• Consider paper trading before going live")

if __name__ == "__main__":
    main()