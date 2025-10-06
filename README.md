# Crypto Portfolio MCP Server

A comprehensive **read-only** cryptocurrency portfolio management MCP (Model Context Protocol) server for Binance, Coinbase, and Kraken. Get real-time portfolio analytics, risk metrics, market intelligence, and actionable insights through Claude Desktop or any MCP client.

## 🚀 Features

### Portfolio Management (Tools 1-5)
- ✅ **Total Portfolio Value**: Aggregate value across all exchanges in USD
- ✅ **All Balances**: Complete balance breakdown with USD values
- ✅ **Portfolio Allocation**: Percentage breakdown by coin
- ✅ **Current Prices**: Real-time prices for portfolio coins
- ✅ **Portfolio P&L**: Profit/loss calculations (where available)

### Analytics & Performance (Tools 6-9)
- ✅ **Biggest Movers**: Top winners and losers in your portfolio
- ✅ **Portfolio Performance**: Historical performance metrics

### Price Alerts (Tools 10-11)
- ✅ **Price Alert Check**: One-time price condition checks
- ✅ **Multiple Alerts**: Batch alert checking

### Risk & Diversification (Tools 12-15)
- ✅ **Diversification Score**: 1-10 rating with recommendations
- ✅ **Volatility Risk**: Risk assessment based on holdings
- ✅ **Stablecoin Ratio**: Cash position analysis

### Market Intelligence (Tools 16-22)
- ✅ **Arbitrage Opportunities**: Price differences across exchanges
- ✅ **Liquidity Check**: 24h volume and sellability
- ✅ **Fear & Greed Index**: Market sentiment indicator

### Portfolio Insights (Tools 23-26)
- ✅ **Dust Detection**: Find small-value holdings
- ✅ **Exchange Distribution**: Portfolio spread across exchanges

### Practical Tools (Tools 27-31)
- ✅ **Withdrawal Fees**: Calculate transfer costs

## 📋 Prerequisites

- **Python 3.10+**
- **API Keys** from one or more exchanges:
  - Binance (read-only permissions)
  - Coinbase (view permissions)
  - Kraken (query permissions)

## 🔧 Installation

### 1. Clone or Create Project Directory

```bash
cd /path/to/your/projects
# Project should already exist at crypto-portfolio-mcp/
cd crypto-portfolio-mcp
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up API Keys

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API credentials:

```env
# Binance
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here

# Coinbase
COINBASE_API_KEY=your_coinbase_api_key_here
COINBASE_API_SECRET=your_coinbase_api_secret_here

# Kraken
KRAKEN_API_KEY=your_kraken_api_key_here
KRAKEN_API_SECRET=your_kraken_api_secret_here
```

**Important**: Only add keys for exchanges you use. The server will automatically detect which exchanges are configured.

### 5. Create Logs Directory

```bash
mkdir -p logs
```

## 🔐 API Key Setup Guide

### Binance

1. Log in to [Binance](https://www.binance.com)
2. Go to **API Management**
3. Create a new API key
4. **Permissions**: Enable only **"Read"** permissions (disable trading/withdrawal)
5. Copy API Key and Secret to `.env`

### Coinbase

1. Log in to [Coinbase](https://www.coinbase.com)
2. Go to **Settings** → **API**
3. Create a new API key
4. **Permissions**: Enable only **"wallet:accounts:read"** and **"wallet:transactions:read"**
5. Copy API Key and Secret to `.env`

### Kraken

1. Log in to [Kraken](https://www.kraken.com)
2. Go to **Settings** → **API**
3. Generate new key
4. **Permissions**: Enable only **"Query Funds"** and **"Query Open Orders & Trades"**
5. Copy API Key and Private Key to `.env`

## 📱 Usage with Claude Desktop

### 1. Configure Claude Desktop

Add to your Claude Desktop MCP settings file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "crypto-portfolio": {
      "command": "/path/to/crypto-portfolio-mcp/venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/crypto-portfolio-mcp"
    }
  }
}
```

### 2. Restart Claude Desktop

Completely quit and restart Claude Desktop.

### 3. Start Using Tools

Ask Claude questions like:

```
"What's my total portfolio value?"
"Show me my portfolio allocation"
"What are the biggest movers in my portfolio today?"
"Check if BTC is above $50,000"
"What's my diversification score?"
"Are there any arbitrage opportunities between my exchanges?"
"What's the current crypto fear & greed index?"
```

## 🛠️ Available Tools

### Portfolio Basics

1. **get_total_portfolio_value** - Total value across all exchanges
2. **get_all_balances** - All coin balances with USD values
3. **get_portfolio_allocation** - Allocation breakdown by percentage
4. **get_current_prices** - Real-time prices for coins
5. **calculate_portfolio_pnl** - Profit/loss calculation

### Analytics

6. **get_biggest_movers** - Top gainers and losers
7. **get_portfolio_performance** - Performance metrics over time

### Price Alerts

10. **check_price_alert** - Check single price condition
11. **check_multiple_alerts** - Batch check multiple alerts

### Risk Management

12. **get_diversification_score** - Portfolio diversification rating (1-10)
13. **get_volatility_risk** - Risk assessment
14. **get_stablecoin_ratio** - Stablecoin percentage

### Market Intelligence

19. **check_arbitrage_opportunities** - Price differences across exchanges
20. **check_liquidity** - 24h volume and liquidity ratings
21. **get_fear_greed_index** - Market sentiment (0-100)

### Portfolio Insights

23. **detect_dust** - Find small-value holdings (<$10)
24. **get_exchange_distribution** - Portfolio spread by exchange

### Practical Tools

29. **calculate_withdrawal_fees** - Withdrawal cost calculator

## 🧪 Testing Without API Keys

Enable mock mode for testing:

```env
MOCK_MODE=true
```

This will return sample data without making real API calls.

## 🔍 Troubleshooting

### "No exchanges initialized"

**Solution**: Check that your API keys are correctly set in `.env` file.

### "Failed to initialize [Exchange]"

**Possible causes**:
- Invalid API credentials
- API key permissions not set to read-only
- Network connectivity issues
- Exchange API downtime

**Solution**:
1. Verify API key and secret are correct
2. Check API key has proper read permissions
3. Test network connection
4. Check exchange status page

### Rate Limiting Errors

The server implements automatic rate limiting for each exchange:
- **Binance**: 15 requests/second
- **Coinbase**: 8 requests/second
- **Kraken**: 1 request/second

If you still hit rate limits, the server will automatically retry with exponential backoff.

### Cache Issues

Clear the cache by restarting the server. Cache TTLs:
- **Prices**: 30 seconds
- **Balances**: 60 seconds

## 📊 Example Outputs

### Total Portfolio Value

```json
{
  "total_usd": 45230.50,
  "by_exchange": {
    "binance": 25000.00,
    "coinbase": 15230.50,
    "kraken": 5000.00
  },
  "timestamp": "2025-10-06T10:30:00"
}
```

### Diversification Score

```json
{
  "score": 7.5,
  "rating": "Good",
  "warnings": [],
  "recommendations": "Portfolio is well-diversified",
  "metrics": {
    "hhi": 0.15,
    "max_allocation": 0.25,
    "num_coins": 8
  }
}
```

### Fear & Greed Index

```json
{
  "value": 65,
  "classification": "Greed",
  "description": "Greed - Bullish sentiment",
  "timestamp": "2025-10-06T10:30:00"
}
```

## 🔒 Security Best Practices

1. ✅ **Read-Only Keys**: Only create API keys with read/view permissions
2. ✅ **No Trading**: This server cannot execute trades or withdrawals
3. ✅ **Secure Storage**: Keep `.env` file secure and never commit to git
4. ✅ **IP Whitelisting**: Consider IP restrictions on exchange API keys
5. ✅ **Key Rotation**: Periodically rotate your API keys

## 🚦 Rate Limits

The server implements conservative rate limiting:

| Exchange | Public API | Private API | Server Limit |
|----------|-----------|-------------|--------------|
| Binance  | 1200/min  | 1200/min    | 15/sec       |
| Coinbase | 10/sec    | 10/sec      | 8/sec        |
| Kraken   | Variable  | 1/sec       | 1/sec        |

## 📝 Logging

Logs are written to:
- `logs/crypto_mcp.log` - Detailed application logs
- Console output - Info level and above

## 🤝 Contributing

This is a read-only portfolio management tool. All features focus on analytics and insights, never trading or fund movement.

## 📜 License

MIT License - See LICENSE file for details.

## ⚠️ Disclaimer

This software is for informational purposes only. It does not constitute financial advice. Always verify portfolio values and metrics independently before making investment decisions.

The server operates in **read-only mode** and cannot execute trades, transfers, or withdrawals.

## 🆘 Support

For issues, questions, or feature requests:
1. Check the Troubleshooting section above
2. Review exchange API documentation
3. Check server logs in `logs/crypto_mcp.log`

## 🗺️ Roadmap

Future enhancements may include:
- Historical performance tracking with local database
- Tax loss harvesting recommendations
- Rebalancing suggestions with specific trade instructions
- Email/webhook alerts for price conditions
- Portfolio comparison with market cap weights
- DCA vs lump sum calculators

---

**Built with**:
- [CCXT](https://github.com/ccxt/ccxt) - Unified exchange API
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Model Context Protocol
- Python 3.10+

**Status**: Production-ready ✅
