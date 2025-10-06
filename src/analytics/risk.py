"""Risk metrics and analysis."""

import logging
from typing import Dict, List, Any
import numpy as np

from ..utils.helpers import safe_divide

logger = logging.getLogger(__name__)

# Common stablecoins
STABLECOINS = {"USDT", "USDC", "BUSD", "DAI", "USD", "TUSD", "USDP", "GUSD"}


class RiskAnalytics:
    """Risk calculation and analysis engine."""

    def __init__(self, exchanges: Dict[str, Any]) -> None:
        """
        Initialize risk analytics.

        Args:
            exchanges: Dictionary of exchange client instances
        """
        self.exchanges = exchanges

    def get_diversification_score(self) -> Dict[str, Any]:
        """
        Calculate diversification score (1-10 scale).

        Returns:
            {
                "score": float,
                "rating": str,
                "warnings": [...],
                "recommendations": str
            }
        """
        # Get allocation data
        allocations = self._get_coin_allocations()

        if not allocations:
            return {
                "score": 0.0,
                "rating": "No data",
                "warnings": ["No portfolio data available"],
                "recommendations": "Add funds to your portfolio"
            }

        # Calculate concentration metrics
        max_allocation = max(allocations.values())
        num_coins = len(allocations)

        # Calculate Herfindahl-Hirschman Index (HHI)
        hhi = sum(percentage ** 2 for percentage in allocations.values())

        # Score calculation
        # - Lower HHI is better (more diversified)
        # - More coins is generally better
        # - Penalize high concentration in single coin

        score = 10.0

        # Penalize high concentration
        if max_allocation > 0.5:  # >50% in one coin
            score -= 4.0
        elif max_allocation > 0.3:  # >30% in one coin
            score -= 2.0

        # Penalize high HHI
        if hhi > 0.5:
            score -= 3.0
        elif hhi > 0.3:
            score -= 1.5

        # Reward number of coins
        if num_coins >= 10:
            score += 1.0
        elif num_coins < 3:
            score -= 2.0

        score = max(1.0, min(10.0, score))

        # Generate warnings
        warnings = []
        if max_allocation > 0.3:
            top_coin = max(allocations.items(), key=lambda x: x[1])
            warnings.append(
                f"Over-concentrated in {top_coin[0]} ({top_coin[1]*100:.1f}%). "
                "Consider diversifying."
            )

        if num_coins < 5:
            warnings.append("Portfolio has few assets. Consider diversifying across more coins.")

        # Rating
        if score >= 8:
            rating = "Excellent"
        elif score >= 6:
            rating = "Good"
        elif score >= 4:
            rating = "Fair"
        else:
            rating = "Poor"

        # Recommendations
        recommendations = self._generate_diversification_recommendations(
            allocations, max_allocation, num_coins
        )

        return {
            "score": round(score, 2),
            "rating": rating,
            "warnings": warnings,
            "recommendations": recommendations,
            "metrics": {
                "hhi": round(hhi, 4),
                "max_allocation": round(max_allocation, 4),
                "num_coins": num_coins
            }
        }

    def get_stablecoin_ratio(self) -> Dict[str, Any]:
        """
        Calculate percentage of portfolio in stablecoins.

        Returns:
            {
                "ratio": float,
                "stablecoin_value_usd": float,
                "total_value_usd": float,
                "assessment": str
            }
        """
        stablecoin_value = 0.0
        total_value = 0.0

        for exchange_client in self.exchanges.values():
            try:
                balances = exchange_client.get_balances()

                for symbol, balance_info in balances.items():
                    amount = balance_info["total"]
                    price = exchange_client.get_usd_price(symbol)
                    value = amount * price
                    total_value += value

                    if symbol in STABLECOINS:
                        stablecoin_value += value

            except Exception as e:
                logger.error(f"Error calculating stablecoin ratio: {str(e)}")

        ratio = safe_divide(stablecoin_value, total_value)

        # Assessment
        if ratio >= 0.5:
            assessment = "Very conservative - High cash position"
        elif ratio >= 0.3:
            assessment = "Conservative - Good cash buffer"
        elif ratio >= 0.1:
            assessment = "Balanced - Moderate cash position"
        elif ratio > 0:
            assessment = "Aggressive - Low cash reserves"
        else:
            assessment = "Very aggressive - No stablecoin allocation"

        return {
            "ratio": ratio,
            "stablecoin_value_usd": stablecoin_value,
            "total_value_usd": total_value,
            "assessment": assessment
        }

    def get_volatility_risk(self) -> Dict[str, Any]:
        """
        Assess portfolio risk based on asset volatility.

        Returns:
            {
                "risk_score": float,
                "risk_level": str,
                "volatile_holdings": [...],
                "stable_holdings": [...]
            }
        """
        # This is a simplified version - real volatility would require historical data
        # We'll use proxy metrics: stablecoin = low risk, others = medium/high

        volatile_holdings = []
        stable_holdings = []
        total_value = 0.0
        volatile_value = 0.0

        for exchange_client in self.exchanges.values():
            try:
                balances = exchange_client.get_balances()

                for symbol, balance_info in balances.items():
                    amount = balance_info["total"]
                    price = exchange_client.get_usd_price(symbol)
                    value = amount * price
                    total_value += value

                    if symbol in STABLECOINS:
                        stable_holdings.append({"symbol": symbol, "value_usd": value})
                    else:
                        volatile_holdings.append({"symbol": symbol, "value_usd": value})
                        volatile_value += value

            except Exception as e:
                logger.error(f"Error calculating volatility risk: {str(e)}")

        risk_ratio = safe_divide(volatile_value, total_value)
        risk_score = risk_ratio * 10.0  # Scale to 0-10

        if risk_score >= 8:
            risk_level = "Very High"
        elif risk_score >= 6:
            risk_level = "High"
        elif risk_score >= 4:
            risk_level = "Medium"
        elif risk_score >= 2:
            risk_level = "Low"
        else:
            risk_level = "Very Low"

        return {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "volatile_holdings": sorted(volatile_holdings, key=lambda x: x["value_usd"], reverse=True)[:10],
            "stable_holdings": sorted(stable_holdings, key=lambda x: x["value_usd"], reverse=True)
        }

    def _get_coin_allocations(self) -> Dict[str, float]:
        """Get allocation percentages for all coins."""
        coin_totals: Dict[str, float] = {}
        total_value = 0.0

        for exchange_client in self.exchanges.values():
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

                    total_value += value

            except:
                pass

        # Convert to percentages
        allocations = {}
        for symbol, value in coin_totals.items():
            allocations[symbol] = safe_divide(value, total_value)

        return allocations

    def _generate_diversification_recommendations(
        self,
        allocations: Dict[str, float],
        max_allocation: float,
        num_coins: int
    ) -> str:
        """Generate diversification recommendations."""
        recommendations = []

        if max_allocation > 0.5:
            recommendations.append("Reduce largest position to under 30%")

        if num_coins < 5:
            recommendations.append("Add 3-5 more quality assets")

        if not recommendations:
            recommendations.append("Portfolio is well-diversified")

        return "; ".join(recommendations)
