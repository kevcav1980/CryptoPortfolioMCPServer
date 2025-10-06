#!/bin/bash

# Crypto Portfolio MCP Server Setup Script

echo "🚀 Setting up Crypto Portfolio MCP Server..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created - Please edit it with your API keys"
else
    echo "✓ .env file already exists"
fi

# Create logs directory
mkdir -p logs
echo "✓ Logs directory ready"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your exchange API keys"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Test the server: python -m src.server"
echo "4. Configure Claude Desktop (see README.md)"
echo ""
echo "📖 For detailed instructions, see README.md"
