# Crypto Portfolio MCP Server

A comprehensive read-only cryptocurrency portfolio management server built on the Model Context Protocol (MCP). Supports Binance, Coinbase, and Kraken exchanges with 18+ analytics tools for portfolio tracking, risk assessment, and market intelligence.

## Overview

This MCP server provides real-time cryptocurrency portfolio analytics through Claude Desktop or any MCP-compatible client. It offers read-only access to your exchange accounts, ensuring your funds remain secure while providing deep insights into your holdings.

### Key Features

- Multi-exchange portfolio aggregation (Binance, Coinbase, Kraken)
- Real-time price tracking and alerts
- Risk and diversification analysis
- Market intelligence and sentiment indicators
- Arbitrage opportunity detection
- Portfolio performance metrics

## Quick Start

### Prerequisites

- Python 3.10 or higher
- API keys from supported exchanges (read-only permissions only)
- Claude Desktop (optional, for AI-powered queries)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/lev-corrupted/CryptoPortfolioMCPServer.git
cd CryptoPortfolioMCPServer
```

2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

3. Configure API credentials:
```bash
cp .env.example .env
# Edit .env with your exchange API keys
```

4. Test the configuration:
```bash
source venv/bin/activate
python test_config.py
```

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "crypto-portfolio": {
      "command": "/absolute/path/to/CryptoPortfolioMCPServer/venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/absolute/path/to/CryptoPortfolioMCPServer"
    }
  }
}
```

Replace `/absolute/path/to/` with your actual installation path.

## API Key Setup

### IMPORTANT: Read-Only Permissions Only

Create API keys with read/view permissions only. Never enable trading or withdrawal permissions.

### Binance

1. Log in to Binance and navigate to API Management
2. Create a new API key with only "Read" permissions
3. Copy the API Key and Secret to your `.env` file

### Coinbase

1. Log in to Coinbase and go to Settings > API
2. Create a new API key with only "wallet:accounts:read" and "wallet:transactions:read"
3. Copy credentials to `.env`

### Kraken

1. Log in to Kraken and go to Settings > API
2. Generate a new key with only "Query Funds" and "Query Open Orders & Trades"
3. Copy credentials to `.env`

## Available Tools

The server provides 18 MCP tools across 7 categories:

### Portfolio Management (5 tools)

- `get_total_portfolio_value` - Aggregate portfolio value across all exchanges
- `get_all_balances` - Detailed balance breakdown with USD values
- `get_portfolio_allocation` - Asset allocation percentages
- `get_current_prices` - Real-time cryptocurrency prices
- `calculate_portfolio_pnl` - Profit/loss calculations

### Analytics (2 tools)

- `get_biggest_movers` - Top gaining and losing assets
- `get_portfolio_performance` - Historical performance metrics

### Price Alerts (2 tools)

- `check_price_alert` - Single price condition monitoring
- `check_multiple_alerts` - Batch alert checking

### Risk Management (3 tools)

- `get_diversification_score` - Portfolio diversification rating (1-10)
- `get_volatility_risk` - Risk assessment based on asset volatility
- `get_stablecoin_ratio` - Percentage in stablecoins

### Market Intelligence (3 tools)

- `check_arbitrage_opportunities` - Cross-exchange price differences
- `check_liquidity` - Trading volume and liquidity analysis
- `get_fear_greed_index` - Crypto market sentiment indicator

### Portfolio Insights (2 tools)

- `detect_dust` - Identify small-value holdings
- `get_exchange_distribution` - Portfolio distribution across exchanges

### Practical Tools (1 tool)

- `calculate_withdrawal_fees` - Estimate transfer costs

## Usage Examples

### With Claude Desktop

After configuration, ask Claude natural language questions:

```
"What is my total portfolio value?"
"Show me my portfolio allocation"
"What are the biggest movers in my portfolio today?"
"Is Bitcoin above $50,000?"
"What is my diversification score?"
"Are there any arbitrage opportunities?"
"What is the current crypto fear and greed index?"
```

## Architecture

```
CryptoPortfolioMCPServer/
├── src/
│   ├── server.py              # Main MCP server
│   ├── exchanges/             # Exchange client implementations
│   │   ├── base_exchange.py
│   │   ├── binance_client.py
│   │   ├── coinbase_client.py
│   │   └── kraken_client.py
│   ├── analytics/             # Analytics engines
│   │   ├── portfolio.py
│   │   ├── risk.py
│   │   └── market.py
│   └── utils/                 # Utilities
│       ├── config.py
│       └── helpers.py
├── .github/                   # GitHub templates
├── requirements.txt
├── setup.sh
├── test_config.py
└── .env.example
```

## Technical Details

- **Exchange API Integration:** CCXT library for unified exchange access
- **Caching:** In-memory with configurable TTL (30s prices, 60s balances)
- **Rate Limiting:** Per-exchange limits (Binance: 15/s, Coinbase: 8/s, Kraken: 1/s)
- **Error Handling:** Automatic retry with exponential backoff (3 attempts)
- **Security:** Read-only operations, no trading or withdrawal capabilities

## Configuration

Environment variables in `.env`:

```bash
# Exchange API credentials
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_secret

COINBASE_API_KEY=your_coinbase_api_key
COINBASE_API_SECRET=your_coinbase_secret

KRAKEN_API_KEY=your_kraken_api_key
KRAKEN_API_SECRET=your_kraken_secret

# Optional settings
MOCK_MODE=false
PRICE_CACHE_DURATION=30
BALANCE_CACHE_DURATION=60
```

## Troubleshooting

### "No exchanges initialized"
Check that API keys are correctly set in `.env` file.

### "Failed to initialize [Exchange]"
Verify API key permissions are set to read-only and credentials are correct.

### Rate Limiting Errors
The server implements automatic rate limiting and retry logic.

## Security

**Important Security Practices:**

1. Use read-only API keys exclusively
2. Never commit `.env` file to version control
3. Enable IP whitelisting on exchange API keys (recommended)
4. Rotate API keys periodically
5. Keep dependencies updated

This server cannot execute trades or withdrawals - it only reads portfolio data.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Contributions must:
- Follow existing code patterns
- Include documentation
- Maintain security best practices
- Never add trading/withdrawal functionality

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Disclaimer

This software is for informational purposes only and does not constitute financial advice. Users are solely responsible for their investment decisions. The server operates in read-only mode and cannot execute trades or transfers.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review [CONTRIBUTING.md](CONTRIBUTING.md)
3. Check server logs in `logs/crypto_mcp.log`
4. Open an issue on GitHub

## Built With

- [CCXT](https://github.com/ccxt/ccxt) - Cryptocurrency exchange trading library
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Model Context Protocol
- Python 3.10+
