#!/usr/bin/env python3
"""Quick configuration test script."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import Config


def main():
    """Test configuration and display status."""
    print("🔍 Testing Crypto Portfolio MCP Configuration...\n")

    config = Config()

    print("Configuration Status:")
    print(f"  Mock Mode: {config.mock_mode}")
    print(f"  Price Cache: {config.price_cache_duration}s")
    print(f"  Balance Cache: {config.balance_cache_duration}s")
    print()

    print("Exchange Credentials:")
    exchanges = ["binance", "coinbase", "kraken"]

    for exchange in exchanges:
        creds = config.get_exchange_credentials(exchange)
        enabled = config.is_exchange_enabled(exchange)

        status = "✓ Configured" if creds else "✗ Not configured"
        enabled_str = "Enabled" if enabled else "Disabled"

        print(f"  {exchange.capitalize():10} {status:20} [{enabled_str}]")

    print()

    validation = config.validate()

    if validation["valid"]:
        print("✅ Configuration is valid!")
        enabled = validation.get("enabled_exchanges", [])
        if enabled:
            print(f"   Enabled exchanges: {', '.join(enabled)}")
        else:
            print("   Running in mock mode")
    else:
        print("❌ Configuration has issues:")
        print(f"   Error: {validation.get('error')}")
        print(f"   Suggestion: {validation.get('suggestion')}")

    print()


if __name__ == "__main__":
    main()
