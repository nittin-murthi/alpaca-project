# AI Hedge Fund Trading System

## ⚠️ **IMPORTANT DISCLAIMERS**

🚨 **This is educational software for demonstration purposes only:**

1. **PAPER TRADING ONLY** - Uses Alpaca's paper trading API
2. **NOT FINANCIAL ADVICE** - Educational demonstration only
3. **RISK WARNING** - Trading involves substantial risk of loss
4. **UNREALISTIC EXPECTATIONS** - 10% weekly returns (14,000% annually) are not achievable
5. **THOROUGH TESTING REQUIRED** - Backtest extensively before any live consideration

## 🎯 **System Overview**

A comprehensive AI-powered trading system that combines:
- **Multi-source News Analysis** with sentiment scoring
- **Advanced Technical Indicators** (50+ indicators)
- **Professional Risk Management** with position sizing and stop-losses
- **Machine Learning Integration** for signal generation
- **Real-time Market Monitoring** and automated execution
- **Comprehensive Logging and Reporting**

## ⚡ **Quick Start**

### 1. Setup Environment
```bash
# Clone and setup
git clone <repository>
cd alpaca-project

# Run automated setup
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Configure Credentials
```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

Required credentials:
- **Alpaca API Key** (provided): `PKMTOA2SN17QT455YBCI`
- **Alpaca Secret Key** (you need to get this)
- **News API Key** (optional - get free from newsapi.org)

### 3. Run the System
```bash
# Simulation mode (default)
python main.py

# Enable live trading (NOT RECOMMENDED)
# Set TRADING_ENABLED=true in .env first
python main.py
```

## 🏗️ **Architecture**

```
alpaca-project/
├── config/
│   └── settings.py          # Configuration management
├── src/
│   ├── trading/
│   │   └── alpaca_client.py  # Alpaca API wrapper
│   ├── analysis/
│   │   ├── news_analyzer.py  # News sentiment analysis
│   │   └── technical_indicators.py  # Technical analysis
│   ├── risk_management/
│   │   └── risk_manager.py   # Risk management system
│   └── strategies/
│       └── strategy_manager.py  # Main strategy coordination
├── data/                    # Historical data and cycles
├── logs/                    # System logs
├── reports/                # Daily reports
├── main.py                 # Main application
├── requirements.txt        # Dependencies
└── setup.sh               # Automated setup
```

## 🔧 **Core Components**

### 1. **News Analysis Engine**
- Multi-source RSS feed aggregation
- News API integration
- VADER & TextBlob sentiment analysis
- Relevance scoring and weighting
- Economic calendar integration

### 2. **Technical Analysis Suite**
- **Trend Indicators**: SMA, EMA, MACD, ADX
- **Momentum Oscillators**: RSI, Stochastic, CCI, Williams %R
- **Volatility Indicators**: Bollinger Bands, ATR, Keltner Channels
- **Volume Analysis**: OBV, AD Line, Chaikin Money Flow
- **Pattern Recognition**: Candlestick patterns, Support/Resistance

### 3. **Risk Management System**
- **Position Sizing**: Based on volatility and signal strength
- **Stop Losses**: Automatic 2% stop losses
- **Take Profits**: Automatic 4% profit targets
- **Portfolio Limits**: Max 10 positions, 2% per position
- **Daily Loss Limits**: 5% maximum daily loss
- **Drawdown Monitoring**: Real-time drawdown tracking
- **Value at Risk (VaR)**: 95% confidence interval

### 4. **Strategy Management**
- **Multi-factor Signals**: Technical + Sentiment + Risk scoring
- **Confidence Thresholds**: Minimum 60% confidence to trade
- **Smart Execution**: Market timing and order management
- **Position Monitoring**: Continuous exit signal evaluation
- **Emergency Liquidation**: Automatic risk-based liquidation

## 📊 **Trading Universe**

Default symbols include:
- **Large Cap Stocks**: AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, NFLX
- **ETFs**: SPY, QQQ, IWM
- **Commodities**: GLD, SLV
- **Bonds**: TLT
- **Volatility**: VIX

## ⚙️ **Configuration**

Key settings in `.env`:

### Risk Management
```bash
MAX_POSITION_SIZE=0.02    # 2% of portfolio per position
MAX_DAILY_LOSS=0.05       # 5% maximum daily loss
STOP_LOSS_PERCENT=0.02    # 2% stop loss
TAKE_PROFIT_PERCENT=0.04  # 4% take profit
```

### Trading Parameters
```bash
TRADING_ENABLED=false     # Set to true for live trading
MIN_VOLUME=1000000       # Minimum daily volume
MIN_PRICE=5.0            # Minimum stock price
MAX_PRICE=500.0          # Maximum stock price
```

## 📈 **Performance Monitoring**

### Real-time Metrics
- Portfolio value and P&L
- Active positions and exposure
- Risk alerts and warnings
- Signal strength and confidence

### Daily Reports
- Performance summary
- Risk metrics (Sharpe ratio, VaR, Beta)
- Position analysis
- Trade execution summary

### Comprehensive Logging
- All trading decisions logged
- Risk calculations tracked
- Error handling and alerts
- Performance attribution

## 🛡️ **Safety Features**

### Multi-layered Risk Controls
1. **Pre-trade Risk Checks**: Position limits, concentration limits
2. **Continuous Monitoring**: Stop losses, take profits, time limits
3. **Emergency Protocols**: Automatic liquidation triggers
4. **Daily Limits**: Maximum daily loss protection
5. **Drawdown Protection**: Portfolio drawdown monitoring

### Error Handling
- Comprehensive exception handling
- Automatic retry mechanisms
- Graceful degradation
- Alert notifications

## 🧪 **Testing & Validation**

### Backtesting Capabilities
```python
# Run historical backtests
from src.backtesting.backtest_engine import BacktestEngine

backtest = BacktestEngine()
results = backtest.run(
    start_date='2023-01-01',
    end_date='2024-01-01',
    initial_capital=100000
)
```

### Paper Trading Validation
- All systems tested on paper trading first
- Full position and risk management validation
- Performance tracking and analysis

## 🔍 **Monitoring & Alerts**

### Risk Alerts
- Daily loss approaching limits
- High portfolio concentration
- Large individual position losses
- High Value at Risk conditions

### Performance Monitoring
- Real-time P&L tracking
- Sharpe ratio calculation
- Maximum drawdown monitoring
- Beta calculation vs benchmarks

## 💡 **Usage Examples**

### Running Analysis Only
```python
from src.strategies.strategy_manager import StrategyManager

manager = StrategyManager()
analysis = manager.analyze_market()
signals = manager.generate_signals(analysis)
```

### Custom Risk Parameters
```python
from src.risk_management.risk_manager import RiskManager

risk_manager = RiskManager()
position_size = risk_manager.calculate_position_size(
    symbol='AAPL',
    entry_price=150.0,
    portfolio_value=100000,
    volatility=0.25,
    signal_strength=0.8
)
```

## 🚀 **Advanced Features**

### Machine Learning Integration
- Signal confidence scoring
- Pattern recognition
- Volatility forecasting
- Sentiment trend analysis

### Web Dashboard (Optional)
```bash
# Install dashboard dependencies
pip install dash plotly

# Run dashboard
python dashboard.py
```

### API Integration
- Alpaca Markets API
- News API integration
- Yahoo Finance backup data
- RSS feed aggregation

## 📞 **Support & Troubleshooting**

### Common Issues

1. **API Connection Errors**
   - Verify API keys in `.env`
   - Check internet connectivity
   - Validate Alpaca account status

2. **Missing Dependencies**
   - Run `./setup.sh` again
   - Check virtual environment activation
   - Manually install missing packages

3. **Data Issues**
   - Verify symbol availability
   - Check market hours
   - Review data quality logs

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py
```

## 📋 **Roadmap**

### Planned Enhancements
- [ ] Options trading strategies
- [ ] Cryptocurrency integration
- [ ] Advanced ML models (LSTM, Transformer)
- [ ] Real-time news processing
- [ ] Social media sentiment
- [ ] Alternative data sources
- [ ] Portfolio optimization algorithms
- [ ] Multi-timeframe analysis
- [ ] Pairs trading strategies
- [ ] Mean reversion strategies

## ⚖️ **Legal & Compliance**

- **Educational Purpose**: This software is for educational demonstration only
- **No Investment Advice**: Not intended as investment advice or recommendations
- **Risk Disclosure**: Trading involves substantial risk of loss
- **Regulatory Compliance**: Users responsible for compliance with local regulations
- **Paper Trading**: Strongly recommended to use paper trading only

## 🤝 **Contributing**

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit pull request

## 📄 **License**

This project is licensed under the MIT License - see LICENSE file for details.

---

**Remember: This is educational software. Never risk money you cannot afford to lose. Past performance does not guarantee future results.**
