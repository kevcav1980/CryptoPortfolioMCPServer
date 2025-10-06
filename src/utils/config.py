"""Configuration management for the MCP server."""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for API credentials and settings."""

    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        load_dotenv()

        # Exchange API credentials
        self.binance_key = os.getenv("BINANCE_API_KEY", "")
        self.binance_secret = os.getenv("BINANCE_API_SECRET", "")

        self.coinbase_key = os.getenv("COINBASE_API_KEY", "")
        self.coinbase_secret = os.getenv("COINBASE_API_SECRET", "")

        self.kraken_key = os.getenv("KRAKEN_API_KEY", "")
        self.kraken_secret = os.getenv("KRAKEN_API_SECRET", "")

        # Optional settings
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
        self.price_cache_duration = int(os.getenv("PRICE_CACHE_DURATION", "30"))
        self.balance_cache_duration = int(os.getenv("BALANCE_CACHE_DURATION", "60"))

        # Parse enabled exchanges
        enabled_str = os.getenv("ENABLED_EXCHANGES", "").strip()
        self.enabled_exchanges = [e.strip() for e in enabled_str.split(",") if e.strip()] if enabled_str else []

        logger.info(f"Configuration loaded. Mock mode: {self.mock_mode}")

    def get_exchange_credentials(self, exchange: str) -> Optional[Dict[str, str]]:
        """
        Get API credentials for a specific exchange.

        Args:
            exchange: Exchange name (binance, coinbase, kraken)

        Returns:
            Dictionary with 'key' and 'secret', or None if not configured
        """
        exchange = exchange.lower()

        if exchange == "binance":
            if self.binance_key and self.binance_secret:
                return {"key": self.binance_key, "secret": self.binance_secret}
        elif exchange == "coinbase":
            if self.coinbase_key and self.coinbase_secret:
                return {"key": self.coinbase_key, "secret": self.coinbase_secret}
        elif exchange == "kraken":
            if self.kraken_key and self.kraken_secret:
                return {"key": self.kraken_key, "secret": self.kraken_secret}

        return None

    def is_exchange_enabled(self, exchange: str) -> bool:
        """
        Check if an exchange is enabled.

        Args:
            exchange: Exchange name

        Returns:
            True if exchange has credentials and is enabled
        """
        exchange = exchange.lower()

        # If no specific exchanges are listed, all with credentials are enabled
        if not self.enabled_exchanges:
            return self.get_exchange_credentials(exchange) is not None

        # Check if exchange is in the enabled list and has credentials
        return exchange in self.enabled_exchanges and self.get_exchange_credentials(exchange) is not None

    def get_enabled_exchanges(self) -> List[str]:
        """
        Get list of all enabled exchanges.

        Returns:
            List of exchange names that are configured and enabled
        """
        exchanges = ["binance", "coinbase", "kraken"]
        return [ex for ex in exchanges if self.is_exchange_enabled(ex)]

    def validate(self) -> Dict[str, any]:
        """
        Validate configuration and return status.

        Returns:
            Dictionary with validation results
        """
        enabled = self.get_enabled_exchanges()

        if not enabled and not self.mock_mode:
            logger.warning("No exchanges are configured with valid credentials!")
            return {
                "valid": False,
                "error": "No exchange credentials found",
                "suggestion": "Please set up API keys in .env file"
            }

        logger.info(f"Enabled exchanges: {', '.join(enabled) if enabled else 'None (mock mode)'}")
        return {
            "valid": True,
            "enabled_exchanges": enabled,
            "mock_mode": self.mock_mode
        }
