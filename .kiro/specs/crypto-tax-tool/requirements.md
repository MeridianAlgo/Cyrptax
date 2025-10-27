# Requirements Document

## Introduction

A privacy-focused, open-source cryptocurrency tax calculation tool that processes transaction data from various exchanges, normalizes it to a standard format, calculates capital gains/losses and income using multiple accounting methods, and generates reports compatible with tax software like TurboTax. The tool prioritizes user privacy by performing all processing locally without sending data to external services.

## Glossary

- **Crypto_Tax_Tool**: The complete Python application system for cryptocurrency tax calculations
- **Exchange_Normalizer**: Component that converts exchange-specific CSV/XLSX formats to standardized format
- **Price_Fetcher**: Component that retrieves historical cryptocurrency prices from CoinGecko API
- **Tax_Calculator**: Component that computes capital gains, losses, and taxable income
- **Report_Generator**: Component that creates tax reports in various formats
- **Data_Validator**: Component that checks transaction data for inconsistencies and errors
- **CLI_Interface**: Command-line interface for user interactions
- **FIFO**: First In, First Out accounting method
- **LIFO**: Last In, First Out accounting method  
- **HIFO**: Highest In, First Out accounting method
- **Standard_Transaction_Format**: Normalized data structure with fields: timestamp, type, base_asset, base_amount, quote_asset, quote_amount, fee_amount, fee_asset, notes

## Requirements

### Requirement 1

**User Story:** As a cryptocurrency trader, I want to import transaction data from multiple exchanges, so that I can consolidate all my trading activity for tax reporting.

#### Acceptance Criteria

1. WHEN a user provides a CSV or XLSX file from a supported exchange, THE Exchange_Normalizer SHALL convert the data to Standard_Transaction_Format
2. THE Exchange_Normalizer SHALL support at least 15 major exchanges including Binance, Coinbase, Kraken, Gemini, and KuCoin
3. WHERE an XLSX file is provided, THE Exchange_Normalizer SHALL allow specification of sheet name for processing
4. THE Exchange_Normalizer SHALL handle missing or malformed data by logging warnings and using default values
5. THE Exchange_Normalizer SHALL parse trading pairs and separate base and quote assets correctly

### Requirement 2

**User Story:** As a tax filer, I want the tool to fetch missing price data automatically, so that I don't have to manually research historical cryptocurrency prices.

#### Acceptance Criteria

1. WHEN transaction data lacks price information, THE Price_Fetcher SHALL retrieve historical prices from CoinGecko API
2. THE Price_Fetcher SHALL cache price data locally to minimize API calls
3. IF price fetching fails for a transaction, THEN THE Price_Fetcher SHALL log the failure and continue processing
4. THE Price_Fetcher SHALL support multiple fiat currencies with USD as default
5. THE Price_Fetcher SHALL handle API rate limits gracefully with retry logic

### Requirement 3

**User Story:** As a user concerned about privacy, I want all data processing to happen locally, so that my financial information never leaves my computer.

#### Acceptance Criteria

1. THE Crypto_Tax_Tool SHALL process all transaction data locally without transmitting to external services
2. THE Crypto_Tax_Tool SHALL only make API calls to fetch public price data, never transaction details
3. THE Crypto_Tax_Tool SHALL store all intermediate and final results on the local filesystem
4. THE Crypto_Tax_Tool SHALL not require user authentication or account creation
5. THE Crypto_Tax_Tool SHALL include clear privacy statements in documentation

### Requirement 4

**User Story:** As a taxpayer, I want to calculate capital gains and losses using different accounting methods, so that I can optimize my tax liability legally.

#### Acceptance Criteria

1. THE Tax_Calculator SHALL support FIFO, LIFO, and HIFO accounting methods
2. WHEN calculating gains, THE Tax_Calculator SHALL distinguish between short-term and long-term capital gains
3. THE Tax_Calculator SHALL maintain accurate inventory tracking for each cryptocurrency
4. THE Tax_Calculator SHALL handle partial sales and complex transaction sequences
5. THE Tax_Calculator SHALL calculate taxable income from staking rewards and airdrops

### Requirement 5

**User Story:** As a tax preparer, I want to generate reports compatible with tax software, so that I can easily import the data into my tax filing system.

#### Acceptance Criteria

1. THE Report_Generator SHALL create CSV files formatted for TurboTax import
2. THE Report_Generator SHALL generate PDF summary reports with key tax figures
3. THE Report_Generator SHALL include transaction details with dates, amounts, and gain/loss calculations
4. THE Report_Generator SHALL separate short-term and long-term capital gains in reports
5. THE Report_Generator SHALL provide income summaries for staking and airdrop events

### Requirement 6

**User Story:** As a data-conscious user, I want the tool to validate my transaction data, so that I can identify and correct errors before tax calculations.

#### Acceptance Criteria

1. THE Data_Validator SHALL detect duplicate transactions and warn the user
2. THE Data_Validator SHALL identify negative balances and flag potential errors
3. THE Data_Validator SHALL verify required fields are present in transaction data
4. THE Data_Validator SHALL check for reasonable date ranges and amounts
5. THE Data_Validator SHALL provide detailed error reports with specific issues identified

### Requirement 7

**User Story:** As a command-line user, I want a simple CLI interface, so that I can automate tax calculations and integrate with my existing workflows.

#### Acceptance Criteria

1. THE CLI_Interface SHALL provide commands for normalize, calculate, and report operations
2. THE CLI_Interface SHALL accept file paths, exchange names, and configuration options as arguments
3. THE CLI_Interface SHALL display progress information and results to the user
4. THE CLI_Interface SHALL return appropriate exit codes for success and failure conditions
5. THE CLI_Interface SHALL provide help documentation for all commands and options

### Requirement 8

**User Story:** As an open-source contributor, I want clear project structure and documentation, so that I can understand and extend the codebase.

#### Acceptance Criteria

1. THE Crypto_Tax_Tool SHALL organize code into logical modules with clear separation of concerns
2. THE Crypto_Tax_Tool SHALL include comprehensive unit tests with at least 80% code coverage
3. THE Crypto_Tax_Tool SHALL provide detailed documentation including setup, usage, and API references
4. THE Crypto_Tax_Tool SHALL include example data files and configuration templates
5. THE Crypto_Tax_Tool SHALL follow Python best practices and include type hints where appropriate