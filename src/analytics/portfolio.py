"""Portfolio analytics and calculations."""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..utils.helpers import safe_divide, calculate_percentage_change

logger = logging.getLogger(__name__)


class PortfolioAnalytics:
    """Portfolio calculation and analytics engine."""

    def __init__(self, exchanges: Dict[str, Any]) -> None:
        """
        Initialize portfolio analytics.

        Args:
            exchanges: Dictionary of exchange client instances
        """
        self.exchanges = exchanges

    def get_total_portfolio_value(self) -> Dict[str, Any]:
        """
        Calculate total portfolio value across all exchanges.

        Returns:
            {
                "total_usd": float,
                "by_exchange": {"binance": float, ...},
                "timestamp": str
            }
        """
        by_exchange = {}
        total_usd = 0.0

        for exchange_name, exchange_client in self.exchanges.items():
            try:
                balances = exchange_client.get_balances()
                exchange_value = 0.0

                for symbol, balance_info in balances.items():
                    amount = balance_info["total"]
                    price = exchange_client.get_usd_price(symbol)
                    value = amount * price
                    exchange_value += value

                by_exchange[exchange_name] = exchange_value
                total_usd += exchange_value

            except Exception as e:
                logger.error(f"Error calculating value for {exchange_name}: {str(e)}")
                by_exchange[exchange_name] = 0.0

        return {
            "total_usd": total_usd,
            "by_exchange": by_exchange,
            "timestamp": datetime.now().isoformat()
        }

    def get_all_balances(self) -> Dict[str, Any]:
        """
        Get all balances from all exchanges with USD values.

        Returns:
            {
                "binance": {
                    "BTC": {"free": 0.5, "locked": 0.0, "total": 0.5, "usd_value": 22500.0}
                },
                ...
            }
        """
        all_balances = {}

        for exchange_name, exchange_client in self.exchanges.items():
            try:
                balances = exchange_client.get_balances()
                exchange_balances = {}

                for symbol, balance_info in balances.items():
                    price = exchange_client.get_usd_price(symbol)
                    exchange_balances[symbol] = {
                        "free": balance_info["free"],
                        "locked": balance_info["locked"],
                        "total": balance_info["total"],
                        "usd_value": balance_info["total"] * price
                    }

                all_balances[exchange_name] = exchange_balances

            except Exception as e:
                logger.error(f"Error fetching balances from {exchange_name}: {str(e)}")
                all_balances[exchange_name] = {}

        return all_balances

    def get_portfolio_allocation(self) -> Dict[str, Any]:
        """
        Get portfolio allocation by coin.

        Returns:
            {
                "allocations": [
                    {"symbol": "BTC", "percentage": 0.45, "usd_value": 20000.0},
                    ...
                ],
                "total_coins": 10
            }
        """
        # Aggregate balances across exchanges
        coin_totals: Dict[str, float] = {}

        for exchange_name, exchange_client in self.exchanges.items():
            try:
                balances = exchange_client.get_balances()

                for symbol, balance_info in balances.items():
                    amount = balance_info["total"]
                    price = exchange_client.get_usd_price(symbol)
                    value = amount * price

                    if symbol in coin_totals:
                        coin_totals[symbol] += value
                    else:
                        coin_totals[symbol] = value

            except Exception as e:
                logger.error(f"Error processing {exchange_name} for allocation: {str(e)}")

        # Calculate total value
        total_value = sum(coin_totals.values())

        # Calculate percentages
        allocations = []
        for symbol, value in sorted(coin_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = safe_divide(value, total_value)
            allocations.append({
                "symbol": symbol,
                "percentage": percentage,
                "usd_value": value
            })

        return {
            "allocations": allocations,
            "total_coins": len(allocations)
        }

    def get_current_prices(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get current prices for specified symbols or all portfolio coins.

        Args:
            symbols: Optional list of symbols to get prices for

        Returns:
            {
                "BTC": {"price_usd": 45000.0, "change_24h": 0.05, "timestamp": "..."},
                ...
            }
        """
        if symbols is None:
            # Get all unique symbols from portfolio
            symbols = set()
            for exchange_client in self.exchanges.values():
                try:
                    balances = exchange_client.get_balances()
                    symbols.update(balances.keys())
                except:
                    pass
            symbols = list(symbols)

        prices = {}

        # Use first available exchange for each symbol
        for symbol in symbols:
            for exchange_client in self.exchanges.values():
                try:
                    price = exchange_client.get_usd_price(symbol)
                    if price > 0:
                        # Try to get 24h change
                        try:
                            ticker = exchange_client.get_ticker_price(f"{symbol}/USDT")
                            change_24h = ticker.get("change_24h", 0.0)
                        except:
                            change_24h = 0.0

                        prices[symbol] = {
                            "price_usd": price,
                            "change_24h": change_24h,
                            "timestamp": datetime.now().isoformat()
                        }
                        break
                except:
                    continue

        return prices

    def calculate_portfolio_pnl(self) -> Dict[str, Any]:
        """
        Calculate portfolio profit/loss if cost basis is available.

        Returns:
            {
                "total_pnl_usd": float,
                "total_pnl_percentage": float,
                "by_coin": {...},
                "unrealized": float,
                "realized": float,
                "note": "Limited data available"
            }
        """
        # Note: Most exchanges don't provide detailed cost basis via API
        # This would require tracking order history

        return {
            "total_pnl_usd": 0.0,
            "total_pnl_percentage": 0.0,
            "by_coin": {},
            "unrealized": 0.0,
            "realized": 0.0,
            "note": "PnL calculation requires historical order data. Use get_average_buy_price for available cost basis."
        }

    def get_exchange_distribution(self) -> Dict[str, Any]:
        """
        Get portfolio distribution across exchanges.

        Returns:
            {
                "binance": {"value_usd": 10000.0, "percentage": 0.5, "coin_count": 5},
                ...
            }
        """
        distribution = {}
        total_value = 0.0

        # First pass: calculate values
        for exchange_name, exchange_client in self.exchanges.items():
            try:
                balances = exchange_client.get_balances()
                exchange_value = 0.0
                coin_count = 0

                for symbol, balance_info in balances.items():
                    amount = balance_info["total"]
                    price = exchange_client.get_usd_price(symbol)
                    value = amount * price
                    exchange_value += value
                    coin_count += 1

                distribution[exchange_name] = {
                    "value_usd": exchange_value,
                    "coin_count": coin_count
                }
                total_value += exchange_value

            except Exception as e:
                logger.error(f"Error calculating distribution for {exchange_name}: {str(e)}")

        # Second pass: add percentages
        for exchange_name in distribution:
            distribution[exchange_name]["percentage"] = safe_divide(
                distribution[exchange_name]["value_usd"],
                total_value
            )

        return distribution

    def detect_dust(self, threshold_usd: float = 10.0) -> Dict[str, Any]:
        """
        Detect coins worth less than threshold.

        Args:
            threshold_usd: Value threshold in USD (default $10)

        Returns:
            {
                "dust_assets": [...],
                "total_dust_value_usd": float,
                "count": int
            }
        """
        dust_assets = []
        total_dust_value = 0.0

        for exchange_name, exchange_client in self.exchanges.items():
            try:
                balances = exchange_client.get_balances()

                for symbol, balance_info in balances.items():
                    amount = balance_info["total"]
                    price = exchange_client.get_usd_price(symbol)
                    value = amount * price

                    if 0 < value < threshold_usd:
                        dust_assets.append({
                            "symbol": symbol,
                            "exchange": exchange_name,
                            "amount": amount,
                            "value_usd": value
                        })
                        total_dust_value += value

            except Exception as e:
                logger.error(f"Error detecting dust on {exchange_name}: {str(e)}")

        return {
            "dust_assets": sorted(dust_assets, key=lambda x: x["value_usd"], reverse=True),
            "total_dust_value_usd": total_dust_value,
            "count": len(dust_assets)
        }
