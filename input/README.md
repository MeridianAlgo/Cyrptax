# Input Folder

Place your cryptocurrency exchange CSV or XLSX files here for automatic processing.

## 🚀 Quick Start

1. **Export your data** from your cryptocurrency exchanges
2. **Place the files** in this `input/` folder
3. **Run auto-processing**: `python src/main.py auto-process`

The tool will automatically:
- 🔍 **Detect** which exchange format each file uses
- ❓ **Ask for confirmation** if confidence is low
- 🔄 **Normalize** all files to standard format
- 💰 **Fetch missing prices** from CoinGecko
- 🧹 **Remove duplicates** automatically

## 📁 Supported File Types

- **CSV files** (`.csv`)
- **Excel files** (`.xlsx`)

## 📋 Supported Exchanges

The auto-detection works with 16+ exchanges:

- Binance, Coinbase, Kraken, Gemini, KuCoin
- Bitfinex, Bitstamp, Bittrex, CEX.IO, Crypto.com
- OKX, Bybit, HTX (Huobi), Exodus, Ledger Live, MetaMask

## 💡 Example Files

You can name your files anything you want:
- `binance_2024_trades.csv`
- `coinbase_transactions.xlsx`
- `my_kraken_data.csv`
- `crypto_trades_jan_2024.csv`

## 🔍 How Auto-Detection Works

The tool analyzes:
1. **Column headers** to match exchange-specific formats
2. **Data patterns** to identify exchange characteristics
3. **Transaction types** to confirm exchange identity

Confidence levels:
- **High (70%+)**: Processes automatically
- **Medium (40-70%)**: Asks for confirmation
- **Low (<40%)**: Shows suggestions for manual selection

## 🎯 Next Steps

After placing files here:

```bash
# Option 1: Full auto-processing
python src/main.py auto-process

# Option 2: Detection first, then process
python src/main.py detect --input-dir input
python src/main.py auto-process

# Option 3: Use the quick start script
python quick_start.py
```

## 🛡️ Privacy Note

All processing happens locally on your computer. Your transaction data never leaves your machine - only public price data is fetched from CoinGecko when needed.