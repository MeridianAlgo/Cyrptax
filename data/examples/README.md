# Sample Data Files

This directory contains sample CSV files demonstrating the expected format for various cryptocurrency exchanges.

## Files

### binance_sample.csv
Sample Binance trading data with the following columns:
- `time`: Transaction timestamp
- `type`: Transaction type (buy/sell)
- `base-asset`: Cryptocurrency symbol
- `quantity`: Amount of cryptocurrency
- `quote-asset`: Quote currency (usually USDT)
- `total`: Total value in quote currency
- `fee`: Transaction fee amount
- `fee-currency`: Fee currency

### coinbase_sample.csv
Sample Coinbase trading data with the following columns:
- `Timestamp`: Transaction timestamp
- `Transaction Type`: Type of transaction
- `Asset`: Cryptocurrency symbol
- `Quantity Transacted`: Amount traded
- `Spot Price Currency`: Quote currency
- `Subtotal`: Transaction value
- `Fees and/or Spread`: Transaction fees
- `Notes`: Additional information

### kraken_sample.csv
Sample Kraken trading data with the following columns:
- `time`: Transaction timestamp
- `type`: Transaction type
- `pair`: Trading pair (e.g., XBTUSD)
- `vol`: Volume/amount
- `cost`: Total cost
- `fee`: Transaction fee
- `ledgers`: Ledger reference

## Usage

These sample files can be used to test the crypto tax tool:

```bash
# Test Binance normalization
python src/main.py normalize data/examples/binance_sample.csv binance

# Test Coinbase normalization
python src/main.py normalize data/examples/coinbase_sample.csv coinbase

# Test Kraken normalization
python src/main.py normalize data/examples/kraken_sample.csv kraken
```

## Notes

- All sample data is fictional and for demonstration purposes only
- Dates are in 2024 for testing purposes
- Amounts and prices are realistic but not actual market data
- These files demonstrate the expected format for each exchange

## Adding Your Own Data

To use your own exchange data:

1. Export your transaction history from your exchange
2. Ensure the CSV format matches the expected columns for your exchange
3. Run the normalization command with your file
4. Proceed with tax calculations

For exchange-specific export instructions, refer to your exchange's documentation.