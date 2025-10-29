# Design Document

## Overview

The Crypto Tax Tool is designed as a modular Python application that processes cryptocurrency transaction data through a pipeline architecture. The system follows a clear separation of concerns with distinct components for data normalization, validation, price fetching, tax calculations, and report generation. All processing occurs locally to ensure user privacy, with the only external dependency being the CoinGecko API for historical price data.

## Architecture

### High-Level Architecture

```mermaid
graph TD
    A[CSV/XLSX Files] --> B[Exchange Normalizer]
    B --> C[Data Validator]
    C --> D[Price Fetcher]
    D --> E[Tax Calculator]
    E --> F[Report Generator]
    F --> G[Output Files]
    
    H[CLI Interface] --> B
    H --> E
    H --> F
    
    I[Config Files] --> B
    I --> E
    
    J[CoinGecko API] --> D
```

### Component Architecture

The application follows a layered architecture pattern:

1. **Presentation Layer**: CLI interface for user interactions
2. **Business Logic Layer**: Core tax calculation and data processing logic
3. **Data Access Layer**: File I/O operations and external API calls
4. **Configuration Layer**: Exchange mappings and application settings

### Data Flow

1. User provides exchange CSV/XLSX files via CLI
2. Exchange Normalizer converts to standard format using configuration mappings
3. Data Validator checks for errors and inconsistencies
4. Price Fetcher enriches data with missing historical prices
5. Tax Calculator processes transactions using specified accounting method
6. Report Generator creates output files in requested formats

## Components and Interfaces

### Exchange Normalizer (`src/normalize.py`)

**Purpose**: Convert exchange-specific CSV/XLSX formats to standardized transaction format

**Key Functions**:
- `normalize_csv(input_file, exchange, output_file, options)`: Main normalization function
- `load_mappings(config_path)`: Load exchange field mappings from YAML
- `parse_pair(pair_string)`: Extract base and quote assets from trading pairs
- `fetch_price(asset, date, currency)`: Get historical price for missing data

**Interfaces**:
- Input: CSV/XLSX files, exchange identifier
- Output: Standardized CSV with columns: timestamp, type, base_asset, base_amount, quote_asset, quote_amount, fee_amount, fee_asset, notes
- Configuration: `config/exchanges.yaml` for field mappings

### Data Validator (`src/validate.py`)

**Purpose**: Ensure data quality and identify potential issues

**Key Functions**:
- `validate_df(dataframe, required_columns)`: Main validation function
- `check_duplicates(dataframe)`: Identify duplicate transactions
- `check_balances(dataframe)`: Verify no negative balances occur
- `check_data_types(dataframe)`: Ensure proper data types for calculations

**Validation Rules**:
- Required fields must be present
- Numeric fields must be valid numbers
- Dates must be parseable
- Transaction types must be recognized
- Balances should not go negative for any asset

### Price Fetcher (`src/price_fetch.py`)

**Purpose**: Retrieve historical cryptocurrency prices from external APIs

**Key Functions**:
- `fetch_price(asset, date, vs_currency)`: Get price for specific asset and date
- `batch_fetch_prices(requests)`: Efficiently fetch multiple prices
- `cache_price(asset, date, price)`: Store prices locally to reduce API calls

**API Integration**:
- Primary: CoinGecko API for historical price data
- Fallback: Local cache for previously fetched prices
- Rate limiting: Respect API limits with exponential backoff

### Tax Calculator (`src/calculate.py`)

**Purpose**: Compute capital gains, losses, and taxable income

**Key Functions**:
- `calculate_taxes(input_file, method, currency)`: Main calculation function
- `process_buy_transaction(transaction, inventory)`: Handle purchase transactions
- `process_sell_transaction(transaction, inventory)`: Calculate gains/losses for sales
- `process_income_transaction(transaction)`: Handle staking/airdrop income

**Accounting Methods**:
- **FIFO**: Use oldest lots first for sales
- **LIFO**: Use newest lots first for sales  
- **HIFO**: Use highest cost basis lots first for sales

**Data Structures**:
- Inventory tracking per asset with cost basis and acquisition dates
- Transaction queue for each accounting method
- Gain/loss records with short-term vs long-term classification

### Report Generator (`src/report.py`)

**Purpose**: Create tax reports in various formats

**Key Functions**:
- `generate_turbotax_report(gains_data)`: Create TurboTax-compatible CSV
- `generate_pdf_summary(gains_data, income_data)`: Create PDF summary report
- `generate_detailed_report(all_data)`: Create comprehensive transaction report

**Output Formats**:
- TurboTax CSV: Formatted for direct import into TurboTax software
- PDF Summary: Human-readable summary with key figures
- Detailed CSV: Complete transaction history with calculations

### CLI Interface (`src/main.py`)

**Purpose**: Provide command-line interface for all operations

**Commands**:
- `normalize`: Convert exchange files to standard format
- `calculate`: Perform tax calculations on normalized data
- `report`: Generate various output reports
- `validate`: Run data validation checks

**Command Structure**:
```bash
python src/main.py normalize input.csv binance --output normalized.csv --fetch-prices
python src/main.py calculate normalized.csv --method fifo --currency usd
python src/main.py report --turbotax --pdf
```

## Data Models

### Standard Transaction Format

```python
{
    "timestamp": "2024-01-01T12:00:00",  # ISO format datetime
    "type": "buy",                       # buy, sell, deposit, withdraw, stake, airdrop
    "base_asset": "BTC",                 # Cryptocurrency symbol
    "base_amount": 1.0,                  # Amount of base asset
    "quote_asset": "USD",                # Fiat or quote currency
    "quote_amount": 50000.0,             # Value in quote currency
    "fee_amount": 25.0,                  # Transaction fee amount
    "fee_asset": "USD",                  # Fee currency
    "notes": "Market order"              # Additional information
}
```

### Inventory Lot Structure

```python
{
    "amount": 0.5,                       # Remaining amount in lot
    "cost_basis": 25000.0,               # Total cost for this lot
    "acquisition_date": "2024-01-01",    # When lot was acquired
    "method_priority": 1                 # Priority for HIFO method
}
```

### Gain/Loss Record

```python
{
    "date": "2024-06-01",                # Sale date
    "asset": "BTC",                      # Asset sold
    "amount": 0.5,                       # Amount sold
    "proceeds": 30000.0,                 # Sale proceeds
    "cost_basis": 25000.0,               # Cost basis of sold amount
    "gain_loss": 5000.0,                 # Calculated gain/loss
    "short_term": False,                 # True if held < 1 year
    "method": "fifo"                     # Accounting method used
}
```

## Error Handling

### Exception Hierarchy

- `CryptoTaxError`: Base exception class
  - `DataValidationError`: Invalid or missing data
  - `PriceFetchError`: Unable to retrieve price data
  - `CalculationError`: Error in tax calculations
  - `FileFormatError`: Unsupported file format or structure

### Error Recovery Strategies

1. **Missing Price Data**: Continue processing with warnings, allow manual price entry
2. **Invalid Transactions**: Skip problematic transactions with detailed logging
3. **API Failures**: Use cached data when available, graceful degradation
4. **File Errors**: Provide clear error messages with suggested fixes

### Logging Strategy

- **INFO**: Normal operation progress and results
- **WARNING**: Non-fatal issues that may affect accuracy
- **ERROR**: Serious problems that prevent processing
- **DEBUG**: Detailed information for troubleshooting

Log files stored in `output/logs/` with rotation and configurable levels.

## Testing Strategy

### Unit Testing

- **Test Coverage**: Minimum 80% code coverage across all modules
- **Test Framework**: pytest with fixtures for sample data
- **Mock Objects**: Mock external API calls and file operations
- **Test Data**: Synthetic transaction data covering edge cases

### Integration Testing

- **End-to-End**: Complete workflow from CSV input to report generation
- **API Integration**: Test CoinGecko API integration with rate limiting
- **File Processing**: Test various CSV/XLSX formats and encodings
- **Cross-Platform**: Ensure compatibility across Windows, macOS, and Linux

### Test Organization

```
tests/
 unit/
    test_normalize.py
    test_validate.py
    test_calculate.py
    test_report.py
 integration/
    test_end_to_end.py
    test_api_integration.py
 fixtures/
     sample_data/
     mock_responses/
```

### Performance Testing

- **Large Dataset Handling**: Test with 10,000+ transactions
- **Memory Usage**: Monitor memory consumption during processing
- **API Rate Limits**: Verify proper handling of rate-limited requests
- **File Size Limits**: Test with large CSV/XLSX files

## Security Considerations

### Data Privacy

- **Local Processing**: All sensitive data remains on user's machine
- **No Data Transmission**: Transaction details never sent to external services
- **Secure Storage**: Temporary files use appropriate permissions
- **Data Cleanup**: Option to securely delete intermediate files

### Input Validation

- **File Type Validation**: Verify file extensions and content types
- **Data Sanitization**: Clean input data to prevent injection attacks
- **Size Limits**: Reasonable limits on file sizes and transaction counts
- **Path Traversal**: Prevent directory traversal in file operations

### API Security

- **HTTPS Only**: All external API calls use encrypted connections
- **API Key Management**: Secure handling of any required API keys
- **Rate Limiting**: Respect API provider rate limits and terms of service
- **Error Information**: Avoid exposing sensitive data in error messages

## Configuration Management

### Exchange Mappings (`config/exchanges.yaml`)

Centralized configuration for field mappings between exchange formats and standard format. Supports:
- Field name mappings
- Data transformation rules
- Default values for missing fields
- Exchange-specific parsing logic

### Application Settings (`config/app.conf`)

Global application configuration including:
- Default currency and tax method
- Logging levels and output paths
- API endpoints and timeout settings
- File processing options

### Environment Variables

Support for environment-based configuration:
- `CRYPTO_TAX_LOG_LEVEL`: Override default logging level
- `CRYPTO_TAX_CACHE_DIR`: Custom cache directory location
- `COINGECKO_API_KEY`: Optional API key for enhanced rate limits

## Deployment and Distribution

### Package Structure

```
crypto-tax-tool/
 src/                    # Core application code
 config/                 # Configuration files
 tests/                  # Test suite
 docs/                   # Documentation
 data/examples/          # Sample input files
 output/                 # Generated reports and logs
 requirements.txt        # Python dependencies
 setup.py               # Package installation
 README.md              # User documentation
 LICENSE                # Apache 2.0 license
```

### Installation Methods

1. **Direct Download**: Clone repository and install dependencies
2. **pip Install**: Package for PyPI distribution
3. **Executable**: Standalone executable using PyInstaller
4. **Docker**: Containerized version for consistent environments

### Dependencies

- **Core**: pandas, python-dateutil, pyyaml, requests
- **Reporting**: fpdf, openpyxl
- **Testing**: pytest, pytest-cov
- **CLI**: argparse (built-in)
- **API**: pycoingecko or requests for CoinGecko integration

### Version Management

- **Semantic Versioning**: Major.Minor.Patch format
- **Changelog**: Detailed change log for each release
- **Backward Compatibility**: Maintain compatibility for configuration files
- **Migration Tools**: Scripts for upgrading between major versions