# Free Crypto Tax Tool

A privacy-focused, open-source cryptocurrency tax calculation tool that processes transaction data from various exchanges, calculates capital gains/losses and income, and generates reports compatible with tax software like TurboTax.

## 🔒 Privacy First

All processing happens locally on your machine. Your financial data never leaves your computer - the tool only makes API calls to fetch public price data, never your transaction details.

## ✨ Features

- **Multi-Exchange Support**: Supports 16+ major cryptocurrency exchanges
- **Multiple Tax Methods**: FIFO, LIFO, and HIFO accounting methods
- **Automatic Price Fetching**: Retrieves historical prices from CoinGecko API
- **Data Validation**: Comprehensive checks for data quality and consistency
- **TurboTax Compatible**: Generates reports ready for tax software import
- **CLI Interface**: Command-line interface for automation and scripting
- **Comprehensive Reports**: PDF summaries, detailed CSVs, and JSON exports

## 📋 Supported Exchanges

| Exchange | Status | Notes |
|----------|--------|-------|
| Binance | ✅ | Full support |
| Coinbase | ✅ | Full support |
| Kraken | ✅ | Full support |
| Gemini | ✅ | Full support |
| KuCoin | ✅ | Full support |
| Bitfinex | ✅ | Full support |
| Bitstamp | ✅ | Full support |
| Bittrex | ✅ | Full support |
| CEX.IO | ✅ | Full support |
| Crypto.com | ✅ | Full support |
| OKX | ✅ | Full support |
| Bybit | ✅ | Full support |
| HTX (Huobi) | ✅ | Full support |
| Exodus | ✅ | Full support |
| Ledger Live | ✅ | Full support |
| MetaMask | ✅ | Full support |

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**:
```bash
git clone <repo-url>
cd crypto-tax-tool
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Verify installation**:
```bash
python src/main.py --help
```

## 📖 Quick Start Guide

### Step 1: Normalize Your Exchange Data

Convert your exchange CSV/XLSX files to a standard format:

```bash
# Basic normalization
python src/main.py normalize data/binance_trades.csv binance

# With price fetching for missing data
python src/main.py normalize data/coinbase_trades.csv coinbase --fetch-prices

# Remove duplicates and specify output file
python src/main.py normalize data/kraken_trades.csv kraken --output my_normalized.csv --remove-duplicates

# For XLSX files, specify sheet name
python src/main.py normalize data/trades.xlsx binance --sheet "Trade History"
```

### Step 2: Calculate Taxes

Process your normalized data to calculate capital gains/losses:

```bash
# Using FIFO method (default)
python src/main.py calculate output/normalized.csv

# Using LIFO method
python src/main.py calculate output/normalized.csv --method lifo

# Using HIFO method with different currency
python src/main.py calculate output/normalized.csv --method hifo --currency eur
```

### Step 3: Generate Reports

Create reports for tax filing:

```bash
# Generate TurboTax-compatible CSV
python src/main.py report --turbotax

# Generate PDF summary
python src/main.py report --pdf

# Generate all report types
python src/main.py report --all
```

## 📚 Detailed Usage

### Command Reference

#### `normalize` - Convert exchange data to standard format

```bash
python src/main.py normalize <input_file> <exchange> [options]
```

**Arguments:**
- `input_file`: Path to CSV or XLSX file from exchange
- `exchange`: Exchange name (use `list-exchanges` to see supported)

**Options:**
- `--output, -o`: Output file path (default: output/normalized.csv)
- `--remove-duplicates`: Remove duplicate transactions
- `--fetch-prices`: Fetch missing price data from CoinGecko
- `--sheet`: Sheet name for XLSX files

#### `calculate` - Calculate taxes from normalized data

```bash
python src/main.py calculate <input_file> [options]
```

**Arguments:**
- `input_file`: Path to normalized CSV file

**Options:**
- `--method, -m`: Tax method (fifo, lifo, hifo) - default: fifo
- `--currency, -c`: Tax currency - default: usd

#### `report` - Generate tax reports

```bash
python src/main.py report [options]
```

**Options:**
- `--turbotax`: Generate TurboTax-compatible CSV
- `--pdf`: Generate PDF summary report
- `--detailed`: Generate detailed CSV report
- `--json`: Generate JSON summary
- `--all`: Generate all report types

#### `validate` - Validate transaction data

```bash
python src/main.py validate <input_file>
```

#### `list-exchanges` - Show supported exchanges

```bash
python src/main.py list-exchanges
```

### Tax Calculation Methods

#### FIFO (First In, First Out)
- Uses oldest lots first for sales
- Most common method for tax purposes
- Generally results in higher gains during bull markets

#### LIFO (Last In, First Out)
- Uses newest lots first for sales
- Can help minimize gains in rising markets
- Not allowed in all jurisdictions

#### HIFO (Highest In, First Out)
- Uses highest cost basis lots first
- Minimizes capital gains
- Requires detailed record keeping

### File Formats

#### Input Files
The tool accepts CSV and XLSX files from supported exchanges. Each exchange has a specific format - see `config/exchanges.yaml` for field mappings.

#### Output Files
- **Normalized CSV**: Standard format with columns: timestamp, type, base_asset, base_amount, quote_asset, quote_amount, fee_amount, fee_asset, notes
- **TurboTax CSV**: Ready for import into TurboTax software
- **PDF Summary**: Human-readable summary with key figures
- **Detailed CSV**: Complete transaction history with calculations

## 🔧 Configuration

### Application Settings

Edit `config/app.conf` to customize:

```ini
[app]
default_currency = usd
default_tax_method = fifo
log_level = INFO

[api]
coingecko_base_url = https://api.coingecko.com/api/v3
request_timeout = 30
rate_limit_delay = 1.0
```

### Adding New Exchanges

To add support for a new exchange, edit `config/exchanges.yaml`:

```yaml
new_exchange:
  timestamp: Date
  type: Type
  base_asset: Asset
  base_amount: Amount
  quote_asset: Currency
  quote_amount: Total
  fee_amount: Fee
  fee_asset: Fee Currency
  notes: Notes
```

## 🐛 Troubleshooting

### Common Issues

**"Exchange not supported" error:**
- Check spelling of exchange name
- Use `python src/main.py list-exchanges` to see supported exchanges
- Add new exchange mapping to `config/exchanges.yaml`

**Price fetching failures:**
- Check internet connection
- CoinGecko API may be rate-limited
- Some assets may not be available on CoinGecko

**Negative balance warnings:**
- Review transaction data for missing deposits
- Check for incorrect transaction types
- Verify amounts and dates

**Memory issues with large files:**
- Process files in smaller chunks
- Increase available system memory
- Use `--remove-duplicates` to reduce data size

### Logging

Enable verbose logging for debugging:

```bash
python src/main.py --verbose normalize data/trades.csv binance
```

Logs are saved to `output/logs/crypto_tax_tool.log`

## 📊 Example Workflow

Here's a complete example processing Binance and Coinbase data:

```bash
# 1. List supported exchanges
python src/main.py list-exchanges

# 2. Normalize Binance data
python src/main.py normalize data/binance_trades.csv binance --fetch-prices --output binance_normalized.csv

# 3. Normalize Coinbase data  
python src/main.py normalize data/coinbase_trades.csv coinbase --fetch-prices --output coinbase_normalized.csv

# 4. Combine normalized files (manual step - concatenate CSVs)
# cat binance_normalized.csv coinbase_normalized.csv > combined_normalized.csv

# 5. Validate combined data
python src/main.py validate combined_normalized.csv

# 6. Calculate taxes using FIFO
python src/main.py calculate combined_normalized.csv --method fifo

# 7. Generate all reports
python src/main.py report --all
```

## ⚖️ Legal Disclaimer

**IMPORTANT**: This tool is provided for informational purposes only and does not constitute tax, legal, or financial advice. 

- Always consult with a qualified tax professional for your specific situation
- Tax laws vary by jurisdiction and change frequently
- The authors are not responsible for any errors or omissions in tax calculations
- Users are responsible for verifying the accuracy of all calculations
- This tool does not guarantee compliance with any tax regulations

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Adding Exchange Support
1. Fork the repository
2. Add exchange mapping to `config/exchanges.yaml`
3. Test with sample data
4. Submit a pull request

### Reporting Issues
- Use GitHub Issues for bug reports
- Include sample data (anonymized) when possible
- Specify your operating system and Python version

### Development Setup
```bash
# Clone and setup development environment
git clone <repo-url>
cd crypto-tax-tool
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Check code style
flake8 src/
```

## 📄 License

Licensed under the Apache License 2.0. See [LICENSE](../LICENSE) for full details.

## 🙏 Acknowledgments

- [CoinGecko](https://coingecko.com) for providing free cryptocurrency price data
- The open-source community for various Python libraries used in this project
- Contributors who have helped improve exchange support and features

---

**Star this repository if you find it useful! ⭐**