"""Main MCP server for crypto portfolio management."""

import logging
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .utils.config import Config
from .utils.helpers import CacheManager, safe_divide, calculate_percentage_change
from .exchanges.binance_client import BinanceClient
from .exchanges.coinbase_client import CoinbaseClient
from .exchanges.kraken_client import KrakenClient
from .analytics.portfolio import PortfolioAnalytics
from .analytics.risk import RiskAnalytics, STABLECOINS
from .analytics.market import MarketAnalytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/crypto_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize server
app = Server("crypto-portfolio-mcp")

# Global state
config: Optional[Config] = None
cache: Optional[CacheManager] = None
exchanges: Dict[str, Any] = {}
portfolio_analytics: Optional[PortfolioAnalytics] = None
risk_analytics: Optional[RiskAnalytics] = None
market_analytics: Optional[MarketAnalytics] = None


def initialize_server() -> None:
    """Initialize the server with exchange clients and analytics engines."""
    global config, cache, exchanges, portfolio_analytics, risk_analytics, market_analytics

    logger.info("Initializing Crypto Portfolio MCP Server...")

    # Load configuration
    config = Config()
    validation = config.validate()

    if not validation["valid"] and not config.mock_mode:
        logger.error("Configuration validation failed!")
        logger.error(f"Error: {validation.get('error')}")
        logger.error(f"Suggestion: {validation.get('suggestion')}")
        sys.exit(1)

    # Initialize cache
    cache = CacheManager()

    # Initialize exchange clients
    exchanges = {}

    if config.is_exchange_enabled("binance"):
        creds = config.get_exchange_credentials("binance")
        if creds:
            try:
                exchanges["binance"] = BinanceClient(
                    creds["key"], creds["secret"], cache, config.mock_mode
                )
                logger.info("✓ Binance client initialized")
            except Exception as e:
                logger.error(f"✗ Failed to initialize Binance: {str(e)}")

    if config.is_exchange_enabled("coinbase"):
        creds = config.get_exchange_credentials("coinbase")
        if creds:
            try:
                exchanges["coinbase"] = CoinbaseClient(
                    creds["key"], creds["secret"], cache, config.mock_mode
                )
                logger.info("✓ Coinbase client initialized")
            except Exception as e:
                logger.error(f"✗ Failed to initialize Coinbase: {str(e)}")

    if config.is_exchange_enabled("kraken"):
        creds = config.get_exchange_credentials("kraken")
        if creds:
            try:
                exchanges["kraken"] = KrakenClient(
                    creds["key"], creds["secret"], cache, config.mock_mode
                )
                logger.info("✓ Kraken client initialized")
            except Exception as e:
                logger.error(f"✗ Failed to initialize Kraken: {str(e)}")

    if not exchanges:
        logger.warning("No exchanges initialized! Running in limited mode.")

    # Initialize analytics engines
    portfolio_analytics = PortfolioAnalytics(exchanges)
    risk_analytics = RiskAnalytics(exchanges)
    market_analytics = MarketAnalytics(exchanges)

    logger.info(f"Server initialized with {len(exchanges)} exchange(s)")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        # Phase 1: Portfolio Basics (1-5)
        Tool(
            name="get_total_portfolio_value",
            description="Get total portfolio value in USD across all exchanges",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="get_all_balances",
            description="Get all coin balances from all exchanges with USD values",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="get_portfolio_allocation",
            description="Get portfolio allocation breakdown by coin with percentages",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="get_current_prices",
            description="Get real-time prices for specified coins or all portfolio coins",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of coin symbols (e.g., ['BTC', 'ETH']). If not provided, returns prices for all portfolio coins."
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="calculate_portfolio_pnl",
            description="Calculate total profit/loss for the portfolio (limited by exchange API availability)",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),

        # Phase 2: Analytics (6-9)
        Tool(
            name="get_biggest_movers",
            description="Get top winning and losing coins in your portfolio by price change",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeframe": {
                        "type": "string",
                        "enum": ["24h", "7d", "30d"],
                        "description": "Time period for price changes"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results per category (default: 5)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_portfolio_performance",
            description="Get portfolio performance metrics over time",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeframe": {
                        "type": "string",
                        "enum": ["24h", "7d", "30d", "90d"],
                        "description": "Time period for performance analysis"
                    }
                },
                "required": []
            }
        ),

        # Price Alerts (10-11)
        Tool(
            name="check_price_alert",
            description="Check if a price alert condition is met for a specific coin",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Coin symbol (e.g., 'BTC')"},
                    "condition": {"type": "string", "enum": ["above", "below"], "description": "Alert condition"},
                    "target_price": {"type": "number", "description": "Target price in USD"}
                },
                "required": ["symbol", "condition", "target_price"]
            }
        ),
        Tool(
            name="check_multiple_alerts",
            description="Check multiple price alerts at once",
            inputSchema={
                "type": "object",
                "properties": {
                    "alerts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "symbol": {"type": "string"},
                                "condition": {"type": "string"},
                                "target_price": {"type": "number"}
                            }
                        },
                        "description": "List of alerts to check"
                    }
                },
                "required": ["alerts"]
            }
        ),

        # Risk & Diversification (12-15)
        Tool(
            name="get_diversification_score",
            description="Get diversification score (1-10) with warnings and recommendations",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="get_volatility_risk",
            description="Assess portfolio risk based on asset volatility",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="get_stablecoin_ratio",
            description="Get percentage of portfolio in stablecoins",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),

        # Market Intelligence (19-22)
        Tool(
            name="check_arbitrage_opportunities",
            description="Find price differences for the same coin across exchanges",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_profit_percentage": {
                        "type": "number",
                        "description": "Minimum profit percentage to report (default: 1.0)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="check_liquidity",
            description="Check 24h trading volume and liquidity for portfolio coins",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="get_fear_greed_index",
            description="Get current crypto market fear & greed index (0-100)",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),

        # Portfolio Insights (23-26)
        Tool(
            name="detect_dust",
            description="Find coins worth less than a threshold (default $10)",
            inputSchema={
                "type": "object",
                "properties": {
                    "threshold_usd": {
                        "type": "number",
                        "description": "Value threshold in USD (default: 10.0)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_exchange_distribution",
            description="Get portfolio value distribution across exchanges",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),

        # Practical Tools (29-31)
        Tool(
            name="calculate_withdrawal_fees",
            description="Calculate cost to withdraw a coin from an exchange",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Coin symbol"},
                    "exchange": {"type": "string", "enum": ["binance", "coinbase", "kraken"], "description": "Exchange name"},
                    "amount": {"type": "number", "description": "Amount to withdraw"}
                },
                "required": ["symbol", "exchange", "amount"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        logger.info(f"Tool called: {name} with arguments: {arguments}")

        result = None

        # Phase 1: Portfolio Basics
        if name == "get_total_portfolio_value":
            result = portfolio_analytics.get_total_portfolio_value()

        elif name == "get_all_balances":
            result = portfolio_analytics.get_all_balances()

        elif name == "get_portfolio_allocation":
            result = portfolio_analytics.get_portfolio_allocation()

        elif name == "get_current_prices":
            symbols = arguments.get("symbols")
            result = portfolio_analytics.get_current_prices(symbols)

        elif name == "calculate_portfolio_pnl":
            result = portfolio_analytics.calculate_portfolio_pnl()

        # Phase 2: Analytics
        elif name == "get_biggest_movers":
            timeframe = arguments.get("timeframe", "24h")
            limit = arguments.get("limit", 5)
            result = market_analytics.get_biggest_movers(timeframe, limit)

        elif name == "get_portfolio_performance":
            timeframe = arguments.get("timeframe", "24h")
            # Simplified performance - would need historical data for full implementation
            result = {
                "timeframe": timeframe,
                "note": "Full historical performance requires order history analysis",
                "current_value": portfolio_analytics.get_total_portfolio_value()
            }

        # Price Alerts
        elif name == "check_price_alert":
            result = market_analytics.check_price_alert(
                arguments["symbol"],
                arguments["condition"],
                arguments["target_price"]
            )

        elif name == "check_multiple_alerts":
            result = market_analytics.check_multiple_alerts(arguments["alerts"])

        # Risk & Diversification
        elif name == "get_diversification_score":
            result = risk_analytics.get_diversification_score()

        elif name == "get_volatility_risk":
            result = risk_analytics.get_volatility_risk()

        elif name == "get_stablecoin_ratio":
            result = risk_analytics.get_stablecoin_ratio()

        # Market Intelligence
        elif name == "check_arbitrage_opportunities":
            min_profit = arguments.get("min_profit_percentage", 1.0)
            result = market_analytics.check_arbitrage_opportunities(min_profit)

        elif name == "check_liquidity":
            result = market_analytics.check_liquidity()

        elif name == "get_fear_greed_index":
            result = market_analytics.get_fear_greed_index()

        # Portfolio Insights
        elif name == "detect_dust":
            threshold = arguments.get("threshold_usd", 10.0)
            result = portfolio_analytics.detect_dust(threshold)

        elif name == "get_exchange_distribution":
            result = portfolio_analytics.get_exchange_distribution()

        # Practical Tools
        elif name == "calculate_withdrawal_fees":
            symbol = arguments["symbol"]
            exchange_name = arguments["exchange"]
            amount = arguments["amount"]

            if exchange_name not in exchanges:
                result = {"error": f"Exchange {exchange_name} not available"}
            else:
                exchange_client = exchanges[exchange_name]
                fee = exchange_client.get_withdrawal_fee(symbol)
                price = exchange_client.get_usd_price(symbol)

                result = {
                    "symbol": symbol,
                    "exchange": exchange_name,
                    "amount": amount,
                    "fee": fee,
                    "fee_usd": fee * price,
                    "fee_percentage": safe_divide(fee, amount),
                    "net_amount": amount - fee
                }

        else:
            result = {"error": f"Unknown tool: {name}"}

        import json
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Error executing {name}: {str(e)}", exc_info=True)
        error_result = {
            "error": str(e),
            "tool": name,
            "suggestion": "Check your API credentials and network connection"
        }
        import json
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


async def main() -> None:
    """Main entry point for the MCP server."""
    initialize_server()

    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server running on stdio")
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
