"""Base exchange class for unified exchange interactions."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging
import time
import ccxt

from ..utils.helpers import CacheManager, RateLimiter, retry_with_backoff

logger = logging.getLogger(__name__)


class BaseExchange(ABC):
    """Abstract base class for exchange clients."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        cache_manager: CacheManager,
        rate_limiter: RateLimiter,
        mock_mode: bool = False
    ) -> None:
        """
        Initialize exchange client.

        Args:
            api_key: API key for authentication
            api_secret: API secret for authentication
            cache_manager: Shared cache manager instance
            rate_limiter: Rate limiter for this exchange
            mock_mode: Enable mock mode for testing
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.cache = cache_manager
        self.rate_limiter = rate_limiter
        self.mock_mode = mock_mode
        self.exchange: Optional[ccxt.Exchange] = None
        self.exchange_name = self.__class__.__name__.replace("Client", "").lower()

        if not mock_mode:
            self._init_exchange()

    @abstractmethod
    def _init_exchange(self) -> None:
        """Initialize the CCXT exchange instance."""
        pass

    @abstractmethod
    def get_exchange_name(self) -> str:
        """Get the exchange name."""
        pass

    @retry_with_backoff(max_attempts=3)
    def get_balances(self) -> Dict[str, Dict[str, float]]:
        """
        Fetch all non-zero balances from the exchange.

        Returns:
            Dictionary mapping symbols to balance info:
            {
                "BTC": {"free": 0.5, "locked": 0.1, "total": 0.6},
                "ETH": {"free": 10.0, "locked": 0.0, "total": 10.0}
            }
        """
        if self.mock_mode:
            return self._get_mock_balances()

        cache_key = f"{self.exchange_name}_balances"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        try:
            self.rate_limiter.wait()
            balance_data = self.exchange.fetch_balance()  # type: ignore

            balances = {}
            for symbol, amounts in balance_data.get("total", {}).items():
                if amounts > 0:  # Only include non-zero balances
                    balances[symbol] = {
                        "free": balance_data.get("free", {}).get(symbol, 0.0),
                        "locked": balance_data.get("used", {}).get(symbol, 0.0),
                        "total": amounts
                    }

            self.cache.set(cache_key, balances, ttl=60)  # Cache for 60 seconds
            logger.info(f"{self.exchange_name}: Fetched {len(balances)} non-zero balances")
            return balances

        except Exception as e:
            logger.error(f"{self.exchange_name}: Error fetching balances: {str(e)}")
            raise Exception(
                f"Failed to fetch balances from {self.exchange_name}: {str(e)}"
            )

    @retry_with_backoff(max_attempts=3)
    def get_ticker_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current ticker price for a symbol.

        Args:
            symbol: Trading pair symbol (e.g., "BTC/USDT")

        Returns:
            Dictionary with price information
        """
        if self.mock_mode:
            return self._get_mock_ticker(symbol)

        cache_key = f"{self.exchange_name}_ticker_{symbol}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        try:
            self.rate_limiter.wait()
            ticker = self.exchange.fetch_ticker(symbol)  # type: ignore

            result = {
                "symbol": symbol,
                "price": ticker.get("last", 0.0),
                "change_24h": ticker.get("percentage", 0.0) / 100.0,  # Convert to decimal
                "high_24h": ticker.get("high", 0.0),
                "low_24h": ticker.get("low", 0.0),
                "volume_24h": ticker.get("baseVolume", 0.0),
                "timestamp": ticker.get("timestamp", 0)
            }

            self.cache.set(cache_key, result, ttl=30)  # Cache for 30 seconds
            return result

        except Exception as e:
            logger.error(f"{self.exchange_name}: Error fetching ticker for {symbol}: {str(e)}")
            raise Exception(
                f"Failed to fetch ticker from {self.exchange_name} for {symbol}: {str(e)}"
            )

    def get_usd_price(self, symbol: str) -> float:
        """
        Get USD price for a symbol.

        Args:
            symbol: Coin symbol (e.g., "BTC")

        Returns:
            Price in USD
        """
        if symbol in ["USDT", "USDC", "BUSD", "DAI", "USD"]:
            return 1.0

        # Try common USD pairs
        for quote in ["USDT", "USD", "USDC"]:
            pair = f"{symbol}/{quote}"
            try:
                ticker = self.get_ticker_price(pair)
                return ticker.get("price", 0.0)
            except:
                continue

        logger.warning(f"Could not get USD price for {symbol} on {self.exchange_name}")
        return 0.0

    def get_all_usd_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get USD prices for multiple symbols.

        Args:
            symbols: List of coin symbols

        Returns:
            Dictionary mapping symbols to USD prices
        """
        prices = {}
        for symbol in symbols:
            try:
                prices[symbol] = self.get_usd_price(symbol)
            except Exception as e:
                logger.warning(f"Failed to get price for {symbol}: {str(e)}")
                prices[symbol] = 0.0

        return prices

    @retry_with_backoff(max_attempts=3)
    def get_order_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get order history.

        Args:
            symbol: Optional trading pair to filter
            limit: Maximum number of orders to fetch

        Returns:
            List of order dictionaries
        """
        if self.mock_mode:
            return []

        try:
            self.rate_limiter.wait()
            if symbol:
                orders = self.exchange.fetch_closed_orders(symbol, limit=limit)  # type: ignore
            else:
                orders = self.exchange.fetch_orders(limit=limit)  # type: ignore

            return orders

        except Exception as e:
            logger.error(f"{self.exchange_name}: Error fetching orders: {str(e)}")
            return []

    def _get_mock_balances(self) -> Dict[str, Dict[str, float]]:
        """Get mock balances for testing."""
        return {
            "BTC": {"free": 0.5, "locked": 0.0, "total": 0.5},
            "ETH": {"free": 5.0, "locked": 0.0, "total": 5.0},
            "USDT": {"free": 10000.0, "locked": 0.0, "total": 10000.0}
        }

    def _get_mock_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get mock ticker for testing."""
        mock_prices = {
            "BTC/USDT": 45000.0,
            "ETH/USDT": 3000.0,
            "BTC/USD": 45000.0,
            "ETH/USD": 3000.0
        }

        return {
            "symbol": symbol,
            "price": mock_prices.get(symbol, 100.0),
            "change_24h": 0.05,
            "high_24h": mock_prices.get(symbol, 100.0) * 1.1,
            "low_24h": mock_prices.get(symbol, 100.0) * 0.9,
            "volume_24h": 1000000.0,
            "timestamp": int(time.time() * 1000)
        }
