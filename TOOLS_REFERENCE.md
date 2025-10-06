# MCP Tools Reference

Complete reference for all available tools in the Crypto Portfolio MCP Server.

## 📊 Portfolio Basics (5 tools)

### 1. get_total_portfolio_value
**Description**: Get total portfolio value across all exchanges
**Parameters**: None
**Example**: "What's my total portfolio value?"

**Returns**:
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

---

### 2. get_all_balances
**Description**: Get all coin balances from all exchanges with USD values
**Parameters**: None
**Example**: "Show me all my balances"

**Returns**:
```json
{
  "binance": {
    "BTC": {
      "free": 0.5,
      "locked": 0.0,
      "total": 0.5,
      "usd_value": 22500.00
    }
  }
}
```

---

### 3. get_portfolio_allocation
**Description**: Portfolio allocation breakdown by coin with percentages
**Parameters**: None
**Example**: "What's my portfolio allocation?"

**Returns**:
```json
{
  "allocations": [
    {
      "symbol": "BTC",
      "percentage": 0.45,
      "usd_value": 20000.00
    }
  ],
  "total_coins": 8
}
```

---

### 4. get_current_prices
**Description**: Real-time prices for specified coins
**Parameters**:
- `symbols` (optional): Array of coin symbols

**Example**: "Get current prices for BTC and ETH"

**Returns**:
```json
{
  "BTC": {
    "price_usd": 45000.00,
    "change_24h": 0.05,
    "timestamp": "2025-10-06T10:30:00"
  }
}
```

---

### 5. calculate_portfolio_pnl
**Description**: Calculate total profit/loss
**Parameters**: None
**Example**: "What's my portfolio P&L?"

**Returns**:
```json
{
  "total_pnl_usd": 0.0,
  "total_pnl_percentage": 0.0,
  "note": "PnL requires order history data"
}
```

---

## 📈 Analytics (2 tools)

### 6. get_biggest_movers
**Description**: Top winning and losing coins by price change
**Parameters**:
- `timeframe`: "24h", "7d", or "30d" (default: "24h")
- `limit`: Number of results (default: 5)

**Example**: "Show me biggest movers in the last 24 hours"

**Returns**:
```json
{
  "winners": [
    {
      "symbol": "ETH",
      "change_percentage": 0.15,
      "current_price": 3450.00
    }
  ],
  "losers": [...],
  "timeframe": "24h"
}
```

---

### 7. get_portfolio_performance
**Description**: Portfolio performance metrics over time
**Parameters**:
- `timeframe`: "24h", "7d", "30d", or "90d"

**Example**: "Show my portfolio performance for the last 7 days"

---

## 🔔 Price Alerts (2 tools)

### 10. check_price_alert
**Description**: Check if a price condition is met
**Parameters**:
- `symbol`: Coin symbol (e.g., "BTC")
- `condition`: "above" or "below"
- `target_price`: Target price in USD

**Example**: "Is Bitcoin above $50,000?"

**Returns**:
```json
{
  "triggered": true,
  "current_price": 51000.00,
  "target_price": 50000.00,
  "difference": 1000.00,
  "difference_percentage": 0.02
}
```

---

### 11. check_multiple_alerts
**Description**: Check multiple price alerts at once
**Parameters**:
- `alerts`: Array of alert objects

**Example**: "Check if BTC is above $50k and ETH is below $3k"

**Returns**:
```json
{
  "triggered_alerts": [...],
  "pending_alerts": [...]
}
```

---

## ⚠️ Risk & Diversification (3 tools)

### 12. get_diversification_score
**Description**: Diversification rating (1-10) with recommendations
**Parameters**: None
**Example**: "What's my diversification score?"

**Returns**:
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

---

### 13. get_volatility_risk
**Description**: Portfolio risk assessment based on volatility
**Parameters**: None
**Example**: "What's my volatility risk?"

**Returns**:
```json
{
  "risk_score": 7.5,
  "risk_level": "High",
  "volatile_holdings": [...],
  "stable_holdings": [...]
}
```

---

### 14. get_stablecoin_ratio
**Description**: Percentage of portfolio in stablecoins
**Parameters**: None
**Example**: "What's my stablecoin ratio?"

**Returns**:
```json
{
  "ratio": 0.25,
  "stablecoin_value_usd": 10000.00,
  "total_value_usd": 40000.00,
  "assessment": "Balanced - Moderate cash position"
}
```

---

## 🔍 Market Intelligence (3 tools)

### 19. check_arbitrage_opportunities
**Description**: Find price differences across exchanges
**Parameters**:
- `min_profit_percentage`: Minimum profit % (default: 1.0)

**Example**: "Are there any arbitrage opportunities?"

**Returns**:
```json
{
  "opportunities": [
    {
      "symbol": "BTC",
      "buy_exchange": "kraken",
      "buy_price": 44900.00,
      "sell_exchange": "binance",
      "sell_price": 45500.00,
      "profit_percentage": 0.013
    }
  ]
}
```

---

### 20. check_liquidity
**Description**: 24h trading volume and liquidity check
**Parameters**: None
**Example**: "Check liquidity for my portfolio"

**Returns**:
```json
{
  "BTC": {
    "volume_24h_usd": 25000000000,
    "liquidity_rating": "Very High",
    "can_sell_easily": true
  }
}
```

---

### 21. get_fear_greed_index
**Description**: Current crypto market sentiment (0-100)
**Parameters**: None
**Example**: "What's the crypto fear and greed index?"

**Returns**:
```json
{
  "value": 65,
  "classification": "Greed",
  "timestamp": "2025-10-06T10:30:00",
  "description": "Greed - Bullish sentiment"
}
```

---

## 💎 Portfolio Insights (2 tools)

### 23. detect_dust
**Description**: Find coins worth less than threshold
**Parameters**:
- `threshold_usd`: Value threshold (default: 10.0)

**Example**: "Show me my dust assets"

**Returns**:
```json
{
  "dust_assets": [
    {
      "symbol": "XRP",
      "exchange": "binance",
      "amount": 5.0,
      "value_usd": 2.50
    }
  ],
  "total_dust_value_usd": 15.75,
  "count": 3
}
```

---

### 24. get_exchange_distribution
**Description**: Portfolio value distribution across exchanges
**Parameters**: None
**Example**: "How is my portfolio distributed across exchanges?"

**Returns**:
```json
{
  "binance": {
    "value_usd": 25000.00,
    "percentage": 0.55,
    "coin_count": 8
  }
}
```

---

## 🔧 Practical Tools (1 tool)

### 29. calculate_withdrawal_fees
**Description**: Calculate cost to withdraw coins
**Parameters**:
- `symbol`: Coin symbol
- `exchange`: Exchange name ("binance", "coinbase", "kraken")
- `amount`: Amount to withdraw

**Example**: "What's the fee to withdraw 1 BTC from Binance?"

**Returns**:
```json
{
  "symbol": "BTC",
  "exchange": "binance",
  "amount": 1.0,
  "fee": 0.0005,
  "fee_usd": 22.50,
  "fee_percentage": 0.0005,
  "net_amount": 0.9995
}
```

---

## 💡 Usage Tips

### Natural Language Examples

**Portfolio Overview:**
```
"What's my total crypto portfolio worth?"
"Show me all my balances across exchanges"
"Break down my allocation by percentage"
```

**Price Monitoring:**
```
"Is Bitcoin above $50,000?"
"Check if ETH dropped below $3,000"
"Alert me if BTC is above $60k and ETH is above $4k"
```

**Risk Analysis:**
```
"How diversified is my portfolio?"
"What's my risk level?"
"Do I have too much in one coin?"
"What percentage is in stablecoins?"
```

**Market Intelligence:**
```
"What's the market sentiment right now?"
"Are there arbitrage opportunities?"
"Which coins moved the most today?"
"Can I easily sell all my holdings?"
```

**Portfolio Cleanup:**
```
"Show me my dust assets"
"Which holdings are worth less than $10?"
"How much do I have on each exchange?"
```

---

## 🎯 Best Practices

1. **Start with basics**: Get total value and allocation first
2. **Monitor regularly**: Check biggest movers and alerts daily
3. **Assess risk**: Review diversification and volatility weekly
4. **Find opportunities**: Check arbitrage when prices are volatile
5. **Clean up**: Identify dust periodically to consolidate

---

**Total Tools Available**: 18 core tools
**Categories**: Portfolio (5) | Analytics (2) | Alerts (2) | Risk (3) | Market (3) | Insights (2) | Tools (1)
