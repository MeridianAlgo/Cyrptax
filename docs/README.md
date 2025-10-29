# Free Crypto Tax Tool

A privacy-focused, open-source cryptocurrency tax calculation tool that processes transaction data from various exchanges, calculates capital gains/losses and income, and generates reports compatible with tax software like TurboTax.

## Privacy First

All processing happens locally on your machine. Your financial data never leaves your computer - the tool only makes API calls to fetch public price data, never your transaction details.

## Key Features

- ** Modern Web Interface**: Beautiful, responsive web GUI for easy use
- ** Smart Auto-Detection**: Automatically identifies exchange formats from CSV files
- ** 50+ Exchange Support**: Binance, Coinbase, Kraken, Gemini, KuCoin, and many more
- ** Multiple Tax Methods**: FIFO, LIFO, HIFO, Average Cost, and Specific ID
- ** Automatic Price Fetching**: Historical prices from CoinGecko API
- ** Data Validation**: Comprehensive quality checks and error reporting
- ** Multi-Format Reports**: TurboTax, H&R Block, TaxAct, TaxSlayer, Credit Karma, CoinLedger
- ** Blockchain Import**: Direct import from Ethereum, Bitcoin, BSC, Polygon
- ** Portfolio Tracking**: Advanced analytics and performance metrics
- ** Privacy First**: All processing happens locally on your computer
- ** CLI Interface**: Command-line automation support
- ** Comprehensive Reports**: PDF summaries, detailed CSVs, JSON exports
- ** Drag & Drop Workflow**: Just put files in input/ folder and run!

## Quick Start

### Installation

#### Option 1: Enhanced Setup (Recommended)
```bash
# Clone the repository
git clone <repo-url>
cd crypto-tax-tool

# Run enhanced setup script
python setup_enhanced.py

# Start web interface
python web_interface.py
# Then open: http://localhost:5000
```

#### Option 2: Manual Setup
```bash
# Clone the repository
git clone <repo-url>
cd crypto-tax-tool

# Install dependencies
pip install -r requirements.txt

# Verify installation
python src/main.py --help
```

### Auto-Detection Workflow (RECOMMENDED)

The easiest way to use the tool:

```bash
# 1. Put your CSV/XLSX files in the input/ folder
cp your_exchange_files.csv input/

# 2. Run auto-processing (detects exchange formats automatically)
python src/main.py auto-process

# 3. The tool will:
#    - Auto-detect exchange formats
#    - Ask for confirmation if unsure
#    - Normalize all files
#    - Fetch missing prices
#    - Remove duplicates

# 4. Calculate taxes and generate reports
python src/main.py calculate output/combined_normalized.csv --method fifo
python src/main.py report --all
```

### Super Quick Start

```bash
# Use the automated workflow script
python quick_start.py
```

### Traditional Manual Workflow

```bash
# 1. Normalize exchange data (manual exchange specification)
python src/main.py normalize data/binance_trades.csv binance --fetch-prices

# 2. Calculate taxes
python src/main.py calculate output/normalized.csv --method fifo

# 3. Generate reports
python src/main.py report --all
```

##  Supported Exchanges (50+)

### Major Exchanges
| Exchange | Status | Exchange | Status |
|----------|--------|----------|--------|
| Binance |  | Coinbase |  |
| Kraken |  | Gemini |  |
| KuCoin |  | OKX |  |
| Bybit |  | HTX (Huobi) |  |
| Bitfinex |  | Bitstamp |  |
| Bittrex |  | CEX.IO |  |
| Crypto.com |  | Gate.io |  |
| Poloniex |  | Upbit |  |
| Bithumb |  | MEXC |  |

### DeFi & DEX Platforms
| Platform | Status | Platform | Status |
|----------|--------|----------|--------|
| Uniswap |  | PancakeSwap |  |
| SushiSwap |  | Curve |  |
| Balancer |  | Compound |  |
| Aave |  | 1inch |  |

### Hardware Wallets
| Wallet | Status | Wallet | Status |
|--------|--------|--------|--------|
| Ledger Live |  | Trezor |  |
| MetaMask |  | Trust Wallet |  |
| Atomic Wallet |  | Exodus |  |

### Regional Exchanges
| Exchange | Status | Exchange | Status |
|----------|--------|----------|--------|
| WazirX |  | CoinDCX |  |
| Bitso |  | Bitpanda |  |
| NiceHash |  | More... |  |

## Documentation

### User Guides
- **[Complete User Guide](docs/README.md)** - Detailed usage instructions and examples
- **[Input Formats](docs/input_formats.md)** - Exchange-specific file formats and requirements
- **[FAQ](docs/faq.md)** - Common questions, troubleshooting, and best practices

### Technical Documentation  
- **[API Reference](docs/api.md)** - Complete module and function documentation
- **[Contributing Guide](docs/contributing.md)** - How to contribute code and features
- **[Security Policy](docs/security.md)** - Privacy, security features, and best practices

### Project Information
- **[Credits](docs/credits.md)** - Acknowledgments, libraries, and contributors
- **[Changelog](CHANGELOG.md)** - Version history and release notes
- **[License](LICENSE)** - Apache 2.0 license details

## Commands

### `auto-process` - Auto-detect and process (RECOMMENDED)
```bash
python src/main.py auto-process [--input-dir input] [--output-dir output]
```
Automatically detects exchange formats and processes all files in the input folder.

### `detect` - Detect exchange format
```bash
python src/main.py detect --file <file> [--normalize]
python src/main.py detect --input-dir input
```
Analyze files to identify exchange formats with confidence scores.

### `normalize` - Convert exchange data
```bash
python src/main.py normalize <file> <exchange> [options]
```

### `calculate` - Calculate taxes
```bash
python src/main.py calculate <normalized_file> [--method fifo|lifo|hifo]
```

### `report` - Generate reports
```bash
python src/main.py report [--turbotax] [--pdf] [--all]
```

### `validate` - Check data quality
```bash
python src/main.py validate <file>
```

### `list-exchanges` - Show supported exchanges
```bash
python src/main.py list-exchanges
```

## Example Workflows

### Auto-Detection Workflow (Recommended)

```bash
# 1. Place files in input folder
cp binance_trades.csv coinbase_transactions.csv input/

# 2. Auto-process everything
python src/main.py auto-process

# 3. Calculate taxes
python src/main.py calculate output/combined_normalized.csv --method fifo

# 4. Generate reports
python src/main.py report --all
```

### Detection-First Workflow

```bash
# 1. Detect formats first
python src/main.py detect --input-dir input

# 2. Process with confirmation
python src/main.py auto-process

# 3. Continue with calculations...
```

### Traditional Manual Workflow

```bash
# Process multiple exchanges manually
python src/main.py normalize binance_data.csv binance --output binance_norm.csv
python src/main.py normalize coinbase_data.csv coinbase --output coinbase_norm.csv

# Combine files (manual step - concatenate CSVs)
# Then calculate taxes
python src/main.py calculate combined_data.csv --method fifo

# Generate all reports
python src/main.py report --all
```

## Tax Methods

- **FIFO (First In, First Out)**: Uses oldest lots first - most common method
- **LIFO (Last In, First Out)**: Uses newest lots first - may reduce gains
- **HIFO (Highest In, First Out)**: Uses highest cost lots first - minimizes gains

## Project Structure

```
crypto-tax-tool/
 src/                    # Core application code
 config/                 # Configuration files
 data/examples/          # Sample input files
 docs/                   # Documentation
 tests/                  # Test suite
 output/                 # Generated reports and logs
 requirements.txt        # Dependencies
```

## Legal Disclaimer

**IMPORTANT**: This tool is for informational purposes only and does not constitute tax advice. Always consult with a qualified tax professional for your specific situation. Users are responsible for verifying all calculations and ensuring compliance with applicable tax laws.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/contributing.md) for guidelines on:
- Adding exchange support
- Reporting bugs
- Submitting features
- Development setup

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Acknowledgments

- [CoinGecko](https://coingecko.com) for cryptocurrency price data
- The open-source community for Python libraries
- Contributors who help improve exchange support

---

**Star this repository if you find it useful!**

For detailed documentation, see the [docs/](docs/) directory.