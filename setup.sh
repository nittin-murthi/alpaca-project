#!/bin/bash

# AI Hedge Fund Setup Script
echo "🚀 Setting up AI Hedge Fund Environment..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating project structure..."
mkdir -p {src,data,logs,config,tests,notebooks,models,reports}
mkdir -p src/{trading,analysis,data_sources,strategies,risk_management,backtesting}

# Download NLTK data for sentiment analysis
echo "🧠 Downloading NLTK data..."
python -c "
import nltk
nltk.download('punkt')
nltk.download('vader_lexicon')
nltk.download('stopwords')
"

echo "✅ Setup complete! Activate with: source venv/bin/activate"