#!/bin/bash

# AI Hedge Fund Quick Start Script
echo "🚀 Starting AI Hedge Fund Demo..."
echo "================================="

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $(basename $VIRTUAL_ENV)"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Run the demo
echo "🎯 Running AI Hedge Fund demonstration..."
echo ""
python demo_trading_system.py

echo ""
echo "✅ Demo completed successfully!"
echo "📄 Check AI_HEDGE_FUND_SUMMARY.md for full details"