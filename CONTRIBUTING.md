# Contributing to Crypto Portfolio MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributions.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/CryptoPortfolioMCPServer.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Development Setup

```bash
cd CryptoPortfolioMCPServer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env` file with your exchange API keys:
```bash
cp .env.example .env
# Edit .env with your API keys
```

Test configuration:
```bash
python test_config.py
```

## Project Structure

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
├── requirements.txt
├── setup.sh
└── test_config.py
```

## Guidelines

### Code Style

- Follow PEP 8 conventions
- Use type hints
- Add docstrings to all functions
- Keep functions focused and modular

### Security

**CRITICAL:** This is a read-only portfolio tool. Never add:
- Trading functionality
- Withdrawal capabilities
- Any feature that modifies exchange accounts

### Testing

- Test with mock mode: `MOCK_MODE=true python test_config.py`
- Verify all exchange clients work independently
- Check error handling and edge cases
- Test rate limiting doesn't cause issues

### Documentation

- Update README.md for user-facing changes
- Add code comments for complex logic
- Update tool descriptions if modifying MCP tools

## Pull Request Process

1. Ensure your code passes all tests
2. Update documentation as needed
3. Reference related issues in your PR description
4. Wait for review and address feedback

## Types of Contributions

### Bug Reports

Use the bug report template and include:
- Python version
- OS and version
- Exchange being used
- Error logs
- Steps to reproduce

### Feature Requests

Use the feature request template. Ensure the feature aligns with project goals:
- Read-only operations
- Portfolio analytics and insights
- Security and privacy focused

### Code Contributions

We welcome:
- New analytics tools
- Additional exchange support
- Performance improvements
- Bug fixes
- Documentation improvements
- Enhanced error handling

### What We Don't Accept

- Trading or automated trading features
- Withdrawal functionality
- Features that modify exchange accounts
- Code that violates exchange API terms

## Coding Standards

### Function Documentation

```python
def calculate_metric(
    exchange: str,
    symbol: str
) -> Dict[str, Any]:
    """
    Calculate portfolio metric.

    Args:
        exchange: Exchange name
        symbol: Coin symbol

    Returns:
        Dictionary containing metric values

    Raises:
        ValueError: If exchange or symbol is invalid
    """
    pass
```

### Error Handling

```python
try:
    result = fetch_data(exchange)
except Exception as e:
    logger.error(f"Error: {str(e)}")
    return {
        "error": str(e),
        "suggestion": "Check your API credentials"
    }
```

### MCP Tool Registration

```python
@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    try:
        if name == "your_tool":
            result = your_function(**arguments)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
    except Exception as e:
        logger.error(f"Error in {name}: {str(e)}")
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]
```

## Testing Guidelines

### Manual Testing Checklist

- [ ] Test with mock mode enabled
- [ ] Test with real exchange credentials
- [ ] Test all supported exchanges
- [ ] Verify rate limiting works
- [ ] Check error handling
- [ ] Validate JSON output format
- [ ] Test with Claude Desktop

## Getting Help

- Open an issue with the "question" label
- Check existing issues and discussions
- Review the README and documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Open an issue with the label "question".

Thank you for contributing!
