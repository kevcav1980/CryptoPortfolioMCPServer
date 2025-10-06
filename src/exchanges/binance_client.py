"""Binance exchange client implementation."""

import ccxt
import logging
from typing import Dict, Any

from .base_exchange import BaseExchange
from ..utils.helpers import CacheManager, RateLimiter

logger = logging.getLogger(__name__)


class BinanceClient(BaseExchange):
    """Binance exchange client using CCXT."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        cache_manager: CacheManager,
        mock_mode: bool = False
    ) -> None:
        """
        Initialize Binance client.

        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            cache_manager: Shared cache manager
            mock_mode: Enable mock mode for testing
        """
        # Binance allows 1200 requests per minute = 20 per second
        rate_limiter = RateLimiter(calls_per_second=15.0)  # Conservative limit
        super().__init__(api_key, api_secret, cache_manager, rate_limiter, mock_mode)

    def _init_exchange(self) -> None:
        """Initialize Binance CCXT instance."""
        try:
            self.exchange = ccxt.binance({
                "apiKey": self.api_key,
                "secret": self.api_secret,
                "enableRateLimit": True,
                "options": {
                    "defaultType": "spot",  # Use spot market by default
                    "adjustForTimeDifference": True,
                }
            })

            # Test connection
            self.exchange.load_markets()
            logger.info("Binance client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {str(e)}")
            raise Exception(f"Binance initialization failed: {str(e)}")

    def get_exchange_name(self) -> str:
        """Get exchange name."""
        return "binance"

    def get_24h_volume(self, symbol: str) -> Dict[str, Any]:
        """
        Get 24-hour volume for a symbol.

        Args:
            symbol: Trading pair symbol

        Returns:
            Volume information
        """
        try:
            ticker = self.get_ticker_price(symbol)
            return {
                "symbol": symbol,
                "volume_24h_base": ticker.get("volume_24h", 0.0),
                "volume_24h_usd": ticker.get("volume_24h", 0.0) * ticker.get("price", 0.0)
            }
        except Exception as e:
            logger.error(f"Error fetching 24h volume for {symbol}: {str(e)}")
            return {"symbol": symbol, "volume_24h_base": 0.0, "volume_24h_usd": 0.0}

    def get_withdrawal_fee(self, symbol: str) -> float:
        """
        Get withdrawal fee for a symbol.

        Args:
            symbol: Coin symbol

        Returns:
            Withdrawal fee amount
        """
        if self.mock_mode:
            return 0.0005 if symbol == "BTC" else 0.01

        try:
            self.rate_limiter.wait()
            currencies = self.exchange.fetch_currencies()  # type: ignore

            if symbol in currencies:
                networks = currencies[symbol].get("networks", {})
                # Get the first available network's fee
                for network_info in networks.values():
                    fee = network_info.get("withdraw", {}).get("fee", 0.0)
                    if fee > 0:
                        return fee

            logger.warning(f"Could not get withdrawal fee for {symbol} on Binance")
            return 0.0

        except Exception as e:
            logger.error(f"Error fetching withdrawal fee for {symbol}: {str(e)}")
            return 0.0
