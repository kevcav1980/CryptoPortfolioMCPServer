# Quick Start Guide

Get your Crypto Portfolio MCP Server running in 5 minutes!

## 🏃 Fast Setup

### 1. Run Setup Script

```bash
cd crypto-portfolio-mcp
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create a `.env` file template

### 2. Add Your API Keys

Edit the `.env` file:

```bash
nano .env  # or use your preferred editor
```

Add at least one exchange's API keys:

```env
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
```

**Important**: Use **read-only** API keys! Never give trading permissions.

### 3. Test Configuration

```bash
source venv/bin/activate
python test_config.py
```

You should see:
```
✅ Configuration is valid!
   Enabled exchanges: binance
```

### 4. Configure Claude Desktop

Edit your Claude config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "crypto-portfolio": {
      "command": "/FULL/PATH/TO/crypto-portfolio-mcp/venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/FULL/PATH/TO/crypto-portfolio-mcp"
    }
  }
}
```

Replace `/FULL/PATH/TO/` with your actual path!

### 5. Restart Claude Desktop

Completely quit and restart Claude Desktop.

## ✅ Verify It Works

Open Claude Desktop and ask:

```
"What's my total crypto portfolio value?"
```

or

```
"Show me my portfolio allocation"
```

## 🎯 Common Commands to Try

**Portfolio Overview:**
- "What's my total portfolio value?"
- "Show all my balances"
- "What's my portfolio allocation?"

**Market Intelligence:**
- "What's the crypto fear and greed index?"
- "Are there arbitrage opportunities in my portfolio?"
- "What are the biggest movers today?"

**Risk Management:**
- "What's my diversification score?"
- "What's my stablecoin ratio?"
- "Show me my dust assets"

**Price Alerts:**
- "Is Bitcoin above $50,000?"
- "Check if ETH is below $3,000"

## 🆘 Troubleshooting

### "No exchanges initialized"
→ Check your `.env` file has valid API keys

### "Permission denied"
→ Make sure API keys are read-only
→ Run: `chmod +x setup.sh`

### Claude doesn't see the tools
→ Check the path in `claude_desktop_config.json` is absolute
→ Restart Claude Desktop completely

## 📚 Next Steps

- Read [README.md](README.md) for full documentation
- Check available tools: 20+ portfolio analytics tools
- Set up additional exchanges for arbitrage detection

## 🔒 Security Reminder

✅ Only use **read-only** API keys
✅ Never commit `.env` to version control
✅ This server cannot trade or withdraw funds

---

**Need help?** Check the full README or server logs in `logs/crypto_mcp.log`
