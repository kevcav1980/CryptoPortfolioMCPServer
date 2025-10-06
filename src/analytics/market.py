"""Market analysis and intelligence."""

import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..utils.helpers import retry_with_backoff, calculate_percentage_change

logger = logging.getLogger(__name__)


class MarketAnalytics:
    """Market analysis and intelligence engine."""

    def __init__(self, exchanges: Dict[str, Any]) -> None:
        """
        Initialize market analytics.

        Args:
            exchanges: Dictionary of exchange client instances
        """
        self.exchanges = exchanges

    def get_biggest_movers(self, timeframe: str = "24h", limit: int = 5) -> Dict[str, Any]:
        """
        Get top winners and losers in portfolio.

        Args:
            timeframe: Time period (24h, 7d, 30d)
            limit: Number of results per category

        Returns:
            {"winners": [...], "losers": [...]}
        """
        movers = []

        for exchange_client in self.exchanges.values():
            try:
                balances = exchange_client.get_balances()

                for symbol in balances.keys():
                    try:
                        ticker = exchange_client.get_ticker_price(f"{symbol}/USDT")
                        change = ticker.get("change_24h", 0.0)

                        movers.append({
                            "symbol": symbol,
                            "change_percentage": change,
                            "current_price": ticker.get("price", 0.0)
                        })
                    except:
                        continue

            except Exception as e:
                logger.error(f"Error getting movers: {str(e)}")

        # Sort and split
        movers.sort(key=lambda x: x["change_percentage"], reverse=True)

        return {
            "winners": movers[:limit],
            "losers": movers[-limit:][::-1],
            "timeframe": timeframe
        }

    def check_arbitrage_opportunities(self, min_profit_percentage: float = 1.0) -> Dict[str, Any]:
        """
        Find arbitrage opportunities across exchanges.

        Args:
            min_profit_percentage: Minimum profit percentage to report

        Returns:
            {"opportunities": [...]}
        """
        if len(self.exchanges) < 2:
            return {
                "opportunities": [],
                "note": "Need at least 2 exchanges for arbitrage detection"
            }

        opportunities = []

        # Get all symbols present in portfolio
        all_symbols = set()
        for exchange_client in self.exchanges.values():
            try:
                balances = exchange_client.get_balances()
                all_symbols.update(balances.keys())
            except:
                pass

        # Check price differences
        for symbol in all_symbols:
            prices = {}

            for exchange_name, exchange_client in self.exchanges.items():
                try:
                    price = exchange_client.get_usd_price(symbol)
                    if price > 0:
                        prices[exchange_name] = price
                except:
                    continue

            if len(prices) >= 2:
                min_exchange = min(prices.items(), key=lambda x: x[1])
                max_exchange = max(prices.items(), key=lambda x: x[1])

                profit_percentage = calculate_percentage_change(
                    min_exchange[1],
                    max_exchange[1]
                )

                if profit_percentage >= min_profit_percentage / 100.0:
                    opportunities.append({
                        "symbol": symbol,
                        "buy_exchange": min_exchange[0],
                        "buy_price": min_exchange[1],
                        "sell_exchange": max_exchange[0],
                        "sell_price": max_exchange[1],
                        "profit_percentage": profit_percentage
                    })

        return {
            "opportunities": sorted(opportunities, key=lambda x: x["profit_percentage"], reverse=True)
        }

    def check_liquidity(self) -> Dict[str, Any]:
        """
        Check 24h trading volume for portfolio coins.

        Returns:
            {
                "BTC": {
                    "volume_24h_usd": float,
                    "liquidity_rating": str,
                    "can_sell_easily": bool
                }
            }
        """
        liquidity_data = {}

        for exchange_client in self.exchanges.values():
            try:
                balances = exchange_client.get_balances()

                for symbol in balances.keys():
                    if symbol in liquidity_data:
                        continue  # Already got data from another exchange

                    try:
                        volume_info = exchange_client.get_24h_volume(symbol)
                        volume_usd = volume_info.get("volume_24h_usd", 0.0)

                        # Rate liquidity
                        if volume_usd >= 100_000_000:  # $100M+
                            rating = "Very High"
                            can_sell = True
                        elif volume_usd >= 10_000_000:  # $10M+
                            rating = "High"
                            can_sell = True
                        elif volume_usd >= 1_000_000:  # $1M+
                            rating = "Medium"
                            can_sell = True
                        elif volume_usd >= 100_000:  # $100K+
                            rating = "Low"
                            can_sell = True
                        else:
                            rating = "Very Low"
                            can_sell = False

                        liquidity_data[symbol] = {
                            "volume_24h_usd": volume_usd,
                            "liquidity_rating": rating,
                            "can_sell_easily": can_sell
                        }
                    except:
                        continue

            except Exception as e:
                logger.error(f"Error checking liquidity: {str(e)}")

        return liquidity_data

    @retry_with_backoff(max_attempts=2)
    def get_fear_greed_index(self) -> Dict[str, Any]:
        """
        Get current crypto fear & greed index.

        Returns:
            {
                "value": int,
                "classification": str,
                "timestamp": str,
                "description": str
            }
        """
        try:
            # Using Alternative.me Fear & Greed Index API
            response = requests.get(
                "https://api.alternative.me/fng/",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if "data" in data and len(data["data"]) > 0:
                fng = data["data"][0]
                value = int(fng.get("value", 50))
                classification = fng.get("value_classification", "Unknown")

                # Add description
                if value >= 75:
                    description = "Extreme greed - Market may be overheated"
                elif value >= 55:
                    description = "Greed - Bullish sentiment"
                elif value >= 45:
                    description = "Neutral - Balanced market"
                elif value >= 25:
                    description = "Fear - Bearish sentiment"
                else:
                    description = "Extreme fear - Potential buying opportunity"

                return {
                    "value": value,
                    "classification": classification,
                    "timestamp": fng.get("timestamp", ""),
                    "description": description
                }

        except Exception as e:
            logger.error(f"Error fetching fear & greed index: {str(e)}")

        return {
            "value": 50,
            "classification": "Unknown",
            "timestamp": datetime.now().isoformat(),
            "description": "Unable to fetch fear & greed index",
            "error": "API unavailable"
        }

    def check_price_alert(
        self,
        symbol: str,
        condition: str,
        target_price: float
    ) -> Dict[str, Any]:
        """
        Check if a price alert condition is met.

        Args:
            symbol: Coin symbol
            condition: "above" or "below"
            target_price: Target price in USD

        Returns:
            {
                "triggered": bool,
                "current_price": float,
                "target_price": float,
                "difference": float
            }
        """
        current_price = 0.0

        # Get current price from any exchange
        for exchange_client in self.exchanges.values():
            try:
                current_price = exchange_client.get_usd_price(symbol)
                if current_price > 0:
                    break
            except:
                continue

        if current_price == 0:
            return {
                "triggered": False,
                "current_price": 0.0,
                "target_price": target_price,
                "difference": 0.0,
                "error": f"Could not get price for {symbol}"
            }

        triggered = False
        if condition.lower() == "above":
            triggered = current_price > target_price
        elif condition.lower() == "below":
            triggered = current_price < target_price

        difference = current_price - target_price
        difference_percentage = calculate_percentage_change(target_price, current_price)

        return {
            "triggered": triggered,
            "current_price": current_price,
            "target_price": target_price,
            "difference": difference,
            "difference_percentage": difference_percentage,
            "condition": condition
        }

    def check_multiple_alerts(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check multiple price alerts.

        Args:
            alerts: List of alert dicts with symbol, condition, target_price

        Returns:
            {"triggered_alerts": [...], "pending_alerts": [...]}
        """
        triggered = []
        pending = []

        for alert in alerts:
            result = self.check_price_alert(
                alert["symbol"],
                alert["condition"],
                alert["target_price"]
            )

            alert_with_result = {**alert, **result}

            if result["triggered"]:
                triggered.append(alert_with_result)
            else:
                pending.append(alert_with_result)

        return {
            "triggered_alerts": triggered,
            "pending_alerts": pending
        }
