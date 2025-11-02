# Free Crypto Tax Tool

**Professional-grade cryptocurrency tax calculations - completely FREE!**

## One-Click Solution

**Just drop your CSV files and get professional tax reports in minutes!**

No complex setup, no manual configuration, no subscription fees. This tool rivals paid services like Koinly and CoinMarketCap but is completely free and privacy-focused.

## Key Features

- **Modern Web Interface** - Beautiful, responsive UI that rivals paid services
- **Fully Automated** - One-click processing with intelligent exchange detection
- **ML-based Column Mapping** - Learns headers and maps unknown formats without manual configs
- **50+ Exchange Support** - All major exchanges, DeFi platforms, and hardware wallets
- **Smart Tax Methods** - Automatically selects optimal tax calculation method
- **6 Tax Software Formats** - TurboTax, H&R Block, TaxAct, TaxSlayer, Credit Karma, CoinLedger
- **Blockchain Import** - Direct import from Ethereum, Bitcoin, BSC, Polygon
- **Portfolio Analytics** - Comprehensive portfolio tracking and performance analysis
- **Privacy First** - All processing happens locally on your computer
- **100% Free** - No subscriptions, no hidden fees, no limits

## Quick Start

### Option 1: Web Interface (Recommended)
```bash
# One-time setup
python scripts/setup/quick_start.py

# Start web interface
python crypto_tax_web.py
# Open: http://localhost:5000
```

### Option 2: One-Click Processing
```bash
# Put your CSV files in data/input/
# Then run:
python crypto_tax_auto.py
```

### Option 3: Command Line
```bash
# For advanced users
python crypto_tax_cli.py --help

# Auto-process with ML fallback when detection is low/unknown
python crypto_tax_cli.py auto-process --ml-fallback
```

## Project Structure

```
crypto-tax-tool/
 app/                    # Core application
    core/              # Core processing modules
    web/               # Web interface
    cli/               # Command line interface
 config/                # Configuration files
 data/                  # Data directories
    input/             # Input CSV files
    output/            # Generated reports
    samples/           # Sample data
 docs/                  # Documentation
 templates/             # Web templates
 static/                # Static assets
 tests/                 # Test suite
 scripts/               # Utility scripts
```

## Supported Exchanges

- See `config/exchanges.yaml` for the current list of supported exchanges and platforms.

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Verify Installation
```bash
python crypto_tax_cli.py --help
```

## Usage

### Web Interface
1. Start the web app: `python crypto_tax_web.py`
2. Open your browser: `http://localhost:5000`
3. Drag & drop your CSV files
4. Click "Process Everything Automatically"
5. Download your tax reports

### Command Line
```bash
# Auto-process all files
python crypto_tax_auto.py

# Manual processing
python crypto_tax_cli.py auto-process
python crypto_tax_cli.py calculate data/output/combined_transactions.csv
python crypto_tax_cli.py report --all
```

## Tax Software Compatibility

| Software | Format | Status |
|----------|--------|--------|
| TurboTax | CSV |  |
| H&R Block | CSV |  |
| TaxAct | CSV |  |
| TaxSlayer | CSV |  |
| Credit Karma Tax | CSV |  |
| CoinLedger | CSV |  |

## Privacy & Security

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Disclaimer

This tool is for informational purposes only and does not constitute tax advice. Always consult with a qualified tax professional for your specific situation.

## Acknowledgments

- [CoinGecko](https://coingecko.com) for cryptocurrency price data
- The open-source community for Python libraries
- Contributors who help improve exchange support

---

**Made with  for the crypto community**

[ Star this repository](https://github.com/your-repo/crypto-tax-tool) if you find it useful!
