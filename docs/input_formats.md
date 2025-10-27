# Exchange Input Formats

This document describes the expected CSV/XLSX formats for each supported exchange.

## 📋 General Requirements

All exchange files should be exported as CSV or XLSX format with the following characteristics:
- **UTF-8 encoding** (or compatible)
- **Header row** with column names
- **Consistent date formats** within each file
- **Numeric values** without currency symbols (except where noted)

## 🏦 Supported Exchanges

### Binance

**Export Location:** Wallet > Transaction History > Generate All Statements

**Required Columns:**
- `time`: Transaction timestamp (ISO format preferred)
- `type`: Transaction type (buy, sell, deposit, withdraw)
- `base-asset`: Cryptocurrency symbol (e.g., BTC, ETH)
- `quantity`: Amount of cryptocurrency
- `quote-asset`: Quote currency (usually USDT, BUSD)
- `total`: Total value in quote currency
- `fee`: Transaction fee amount
- `fee-currency`: Fee currency

**Sample Format:**
```csv
time,type,base-asset,quantity,quote-asset,total,fee,fee-currency
2024-01-15T10:30:00,buy,BTC,0.5,USDT,25000.00,12.50,USDT
2024-02-20T14:45:00,sell,BTC,0.2,USDT,11000.00,5.50,USDT
```

### Coinbase

**Export Location:** Portfolio > Statements > Generate Report

**Required Columns:**
- `Timestamp`: Transaction timestamp
- `Transaction Type`: Type (Buy, Sell, Receive, Send)
- `Asset`: Cryptocurrency symbol
- `Quantity Transacted`: Amount traded
- `Spot Price Currency`: Quote currency
- `Subtotal`: Transaction value before fees
- `Fees and/or Spread`: Total fees
- `Notes`: Additional information

**Sample Format:**
```csv
Timestamp,Transaction Type,Asset,Quantity Transacted,Spot Price Currency,Subtotal,Fees and/or Spread,Notes
2024-01-10T08:30:00Z,Buy,BTC,0.25,USD,12500.00,25.00,Market order
```

### Kraken

**Export Location:** History > Export > Trades

**Required Columns:**
- `time`: Transaction timestamp
- `type`: Transaction type (buy, sell)
- `pair`: Trading pair (e.g., XBTUSD, ETHUSD)
- `vol`: Volume/amount
- `cost`: Total cost
- `fee`: Transaction fee
- `ledgers`: Ledger reference ID

**Sample Format:**
```csv
time,type,pair,vol,cost,fee,ledgers
2024-01-08T09:45:00Z,buy,XBTUSD,0.3,15000.00,7.50,L123456
```

**Note:** Kraken uses X/Z prefixes (XBTUSD = BTC/USD). The tool automatically handles this conversion.

### Gemini

**Export Location:** Account > History > Export

**Required Columns:**
- `Date`: Transaction date
- `Type`: Transaction type
- `Symbol`: Cryptocurrency symbol
- `Amount`: Transaction amount
- `USD Amount`: Value in USD
- `Fee (USD)`: Fee in USD
- `Specification`: Additional details

**Sample Format:**
```csv
Date,Type,Symbol,Amount,USD Amount,Fee (USD),Specification
2024-01-12 10:30:00,Buy,BTC,0.4,20000.00,10.00,Market
```

### KuCoin

**Export Location:** Assets > Transaction History > Export

**Required Columns:**
- `Time`: Transaction timestamp
- `Type`: Transaction type
- `Symbol`: Trading pair or asset
- `Filled`: Amount filled
- `Total`: Total value
- `Fee`: Transaction fee
- `Fee Currency`: Fee currency
- `Remark`: Additional notes

**Sample Format:**
```csv
Time,Type,Symbol,Filled,Total,Fee,Fee Currency,Remark
2024-01-14 11:45:00,buy,BTC,0.35,17500.00,8.75,USDT,Market Order
```

### Bitfinex

**Export Location:** Reports > Generate Report

**Required Columns:**
- `Date`: Transaction date
- `Description`: Transaction type/description
- `Pair`: Trading pair
- `Amount`: Transaction amount
- `Price * Amount`: Total value
- `Fee`: Transaction fee
- `Fee Currency`: Fee currency
- `Info`: Additional information

### Bitstamp

**Export Location:** Account > History > Export CSV

**Required Columns:**
- `Datetime`: Transaction timestamp
- `Type`: Transaction type
- `Market`: Trading pair
- `Amount`: Transaction amount
- `Value`: Total value
- `Fee`: Transaction fee
- `Fee currency`: Fee currency

### Bittrex

**Export Location:** Holdings > Orders > Export to CSV

**Required Columns:**
- `Time`: Transaction timestamp
- `Type`: Order type
- `Market`: Trading pair
- `Quantity`: Amount
- `Total`: Total value
- `Fee`: Transaction fee
- `Currency`: Fee currency
- `Uuid`: Order ID

### CEX.IO

**Export Location:** Finance > Transaction History > Export

**Required Columns:**
- `date`: Transaction date
- `type`: Transaction type
- `symbol`: Asset symbol
- `amount`: Transaction amount
- `price * amount`: Total value
- `fee`: Transaction fee
- `fee_currency`: Fee currency
- `order_id`: Order reference

### Crypto.com

**Export Location:** Accounts > Transaction History > Export

**Required Columns:**
- `Time`: Transaction timestamp
- `Side`: Transaction side (buy/sell)
- `Pair`: Trading pair
- `Amount`: Transaction amount
- `Total`: Total value
- `Txhash`: Transaction hash

**Note:** Fee information may be in separate columns or transactions.

### OKX

**Export Location:** Assets > Bills > Export

**Required Columns:**
- `Time`: Transaction timestamp
- `Type`: Transaction type
- `Instrument`: Trading pair
- `Size`: Transaction size
- `Filled`: Filled amount
- `Fee`: Transaction fee
- `Fee Currency`: Fee currency
- `Order ID`: Order reference

### Bybit

**Export Location:** Assets > Transaction History > Export

**Required Columns:**
- `Time`: Transaction timestamp
- `Type`: Transaction type
- `Coin`: Cryptocurrency
- `Change`: Amount change
- `Fee`: Transaction fee
- `Notes`: Additional information

### HTX (Huobi)

**Export Location:** Assets > Transaction History > Export

**Required Columns:**
- `Time`: Transaction timestamp
- `Type`: Transaction type
- `Pair`: Trading pair
- `Amount`: Transaction amount
- `Total`: Total value
- `Fee`: Transaction fee
- `Fee Currency`: Fee currency

### Exodus

**Export Location:** Portfolio > Export > CSV

**Required Columns:**
- `Date`: Transaction date
- `Type`: Transaction type
- `Currency`: Cryptocurrency
- `Amount`: Transaction amount
- `Fee`: Transaction fee
- `TxID`: Transaction ID

### Ledger Live

**Export Location:** Accounts > Export Operations

**Required Columns:**
- `Operation Date`: Transaction date
- `Operation Type`: Transaction type
- `Currency Ticker`: Asset symbol
- `Operation Amount`: Transaction amount
- `Operation Fees`: Transaction fees
- `Operation Hash`: Transaction hash

### MetaMask

**Export Location:** Activity > Export (via third-party tools)

**Required Columns:**
- `Date`: Transaction date
- `Type`: Transaction type
- `Token`: Asset symbol
- `Amount`: Transaction amount
- `Value`: USD value
- `Fee`: Gas fee
- `TxHash`: Transaction hash

## 🔧 Format Variations

### Date Formats

The tool supports various date formats:
- ISO 8601: `2024-01-15T10:30:00Z`
- US format: `01/15/2024 10:30:00`
- European format: `15/01/2024 10:30:00`
- Simple date: `2024-01-15`

### Transaction Types

Common transaction types across exchanges:
- **buy/Buy**: Purchase transactions
- **sell/Sell**: Sale transactions
- **deposit/Deposit**: Incoming transfers
- **withdraw/Withdraw**: Outgoing transfers
- **stake/Staking**: Staking rewards
- **airdrop/Airdrop**: Airdrop receipts
- **fee/Fee**: Fee-only transactions

### Trading Pairs

Trading pairs may be formatted as:
- `BTC/USD`, `ETH/USDT` (with separator)
- `BTCUSD`, `ETHUSDT` (without separator)
- `XBTUSD`, `XETHZUSD` (Kraken format with prefixes)

The tool automatically parses these formats.

## 📝 Preparation Tips

### Before Export

1. **Set date range** to cover your entire tax year
2. **Include all transaction types** (trades, deposits, withdrawals)
3. **Export in chronological order** if possible
4. **Use UTF-8 encoding** to avoid character issues

### After Export

1. **Review the file** for completeness
2. **Check for missing data** (empty cells, zero amounts)
3. **Verify date formats** are consistent
4. **Remove any summary rows** at the top or bottom

### Common Issues

- **Missing headers**: Ensure the first row contains column names
- **Extra columns**: Additional columns are ignored, but required ones must be present
- **Currency symbols**: Remove $ or other symbols from numeric fields
- **Merged cells**: Ensure each transaction is on a separate row
- **Encoding issues**: Save as UTF-8 if you see strange characters

## 🆕 Adding New Exchanges

To add support for a new exchange:

1. **Analyze the CSV format** from the exchange
2. **Map columns** to standard format in `config/exchanges.yaml`
3. **Test with sample data**
4. **Submit a pull request** with the new mapping

### Mapping Template

```yaml
new_exchange:
  timestamp: "Date Column Name"
  type: "Type Column Name"
  base_asset: "Asset Column Name"
  base_amount: "Amount Column Name"
  quote_asset: "Currency Column Name"
  quote_amount: "Value Column Name"
  fee_amount: "Fee Column Name"
  fee_asset: "Fee Currency Column Name"
  notes: "Notes Column Name"
```

Set any unavailable fields to `None`.

## 🔍 Validation

After normalization, the tool validates:
- **Required fields** are present
- **Data types** are correct
- **Dates** are valid
- **Amounts** are numeric
- **No negative balances** occur

Review validation warnings and errors before proceeding with tax calculations.

---

For questions about specific exchange formats, please check the exchange's documentation or contact their support team for export instructions.