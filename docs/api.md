# API Documentation

##  Module Reference

This document provides detailed API documentation for all modules in the Crypto Tax Tool.

##  Core Modules

### `src.auto_detect` - Exchange Format Detection

#### `ExchangeDetector`

Main class for detecting exchange formats from CSV/XLSX files.

```python
class ExchangeDetector:
    def __init__(self):
        """Initialize detector with exchange mappings."""
        
    def detect_exchange(self, file_path: str, sheet_name: Optional[str] = None) -> Tuple[str, float, Dict]:
        """
        Detect exchange format for a file.
        
        Args:
            file_path: Path to CSV or XLSX file
            sheet_name: Sheet name for XLSX files
            
        Returns:
            Tuple of (exchange_name, confidence_score, analysis_details)
        """
        
    def scan_input_folder(self, input_dir: str = "input") -> List[Dict]:
        """
        Scan folder for files and detect their formats.
        
        Args:
            input_dir: Directory to scan
            
        Returns:
            List of detection results
        """
```

#### Functions

```python
def auto_process_input_folder(input_dir: str = "input", output_dir: str = "output", interactive: bool = True) -> List[Dict]:
    """
    Automatically process all files in input folder.
    
    Args:
        input_dir: Input directory path
        output_dir: Output directory path  
        interactive: Whether to ask for user confirmation
        
    Returns:
        List of processing results
    """

def interactive_exchange_selection(file_path: str) -> str:
    """
    Interactive exchange selection for a file.
    
    Args:
        file_path: Path to file to analyze
        
    Returns:
        Selected exchange name
    """
```

### `src.normalize` - Data Normalization

#### Functions

```python
def normalize_csv(
    input_file: str,
    exchange: str,
    output_file: str = 'output/normalized.csv',
    remove_duplicates: bool = False,
    fetch_missing_prices: bool = False,
    sheet_name: Optional[str] = None
) -> None:
    """
    Normalize exchange CSV/XLSX to standard format.
    
    Args:
        input_file: Path to input file
        exchange: Exchange name
        output_file: Output file path
        remove_duplicates: Remove duplicate transactions
        fetch_missing_prices: Fetch missing price data
        sheet_name: Sheet name for XLSX files
    """

def parse_pair(pair: str) -> tuple:
    """
    Parse trading pair string to extract base and quote assets.
    
    Args:
        pair: Trading pair string
        
    Returns:
        Tuple of (base_asset, quote_asset)
    """
```

### `src.calculate` - Tax Calculations

#### `TaxLot`

Represents a tax lot for inventory tracking.

```python
class TaxLot:
    def __init__(self, amount: float, cost_basis: float, acquisition_date: datetime, transaction_id: Optional[str] = None):
        """
        Initialize tax lot.
        
        Args:
            amount: Amount of asset
            cost_basis: Total cost for this lot
            acquisition_date: When lot was acquired
            transaction_id: Optional transaction reference
        """
```

#### `AssetInventory`

Manages inventory for a single asset.

```python
class AssetInventory:
    def __init__(self, asset: str, method: str = 'fifo'):
        """
        Initialize asset inventory.
        
        Args:
            asset: Asset symbol
            method: Accounting method (fifo, lifo, hifo)
        """
        
    def add_lot(self, lot: TaxLot) -> None:
        """Add tax lot to inventory."""
        
    def remove_amount(self, amount: float) -> List[Tuple[TaxLot, float]]:
        """Remove amount from inventory and return lots used."""
```

#### `TaxCalculator`

Main tax calculation engine.

```python
class TaxCalculator:
    def __init__(self, method: str = 'fifo', tax_currency: str = 'usd'):
        """
        Initialize tax calculator.
        
        Args:
            method: Tax accounting method
            tax_currency: Currency for tax calculations
        """
        
    def calculate_taxes(self, input_file: str) -> Tuple[pd.DataFrame, float]:
        """
        Calculate taxes from normalized data.
        
        Args:
            input_file: Path to normalized CSV
            
        Returns:
            Tuple of (gains_losses_df, total_income)
        """
```

#### Functions

```python
def calculate_taxes(input_file: str, method: str = 'fifo', tax_currency: str = 'usd') -> Tuple[pd.DataFrame, float]:
    """
    Convenience function to calculate taxes.
    
    Args:
        input_file: Path to normalized CSV
        method: Tax accounting method
        tax_currency: Currency for calculations
        
    Returns:
        Tuple of (gains_losses_df, total_income)
    """
```

### `src.validate` - Data Validation

#### Functions

```python
def validate_df(df: pd.DataFrame, required_cols: List[str] = None) -> Dict[str, Any]:
    """
    Validate normalized transaction DataFrame.
    
    Args:
        df: Transaction DataFrame
        required_cols: Required column names
        
    Returns:
        Dictionary with validation results
    """

def check_duplicates(df: pd.DataFrame) -> int:
    """
    Check for duplicate transactions.
    
    Args:
        df: Transaction DataFrame
        
    Returns:
        Number of duplicates found
    """

def check_balances(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Check for negative balances.
    
    Args:
        df: Transaction DataFrame
        
    Returns:
        List of negative balance occurrences
    """
```

### `src.price_fetch` - Price Data

#### `PriceFetcher`

Handles cryptocurrency price fetching and caching.

```python
class PriceFetcher:
    def __init__(self):
        """Initialize price fetcher with CoinGecko API."""
        
    def fetch_price(self, asset: str, date: datetime, vs_currency: str = 'usd') -> Optional[float]:
        """
        Fetch historical price for an asset.
        
        Args:
            asset: Asset symbol
            date: Date for price lookup
            vs_currency: Currency to get price in
            
        Returns:
            Price as float or None if not found
        """
        
    def batch_fetch_prices(self, requests_list: list) -> Dict[str, Optional[float]]:
        """
        Fetch multiple prices efficiently.
        
        Args:
            requests_list: List of (asset, date, vs_currency) tuples
            
        Returns:
            Dictionary mapping request keys to prices
        """
```

#### Functions

```python
def fetch_price(asset: str, date: datetime, vs_currency: str = 'usd') -> Optional[float]:
    """
    Convenience function to fetch a single price.
    
    Args:
        asset: Asset symbol
        date: Date for price lookup
        vs_currency: Currency to get price in
        
    Returns:
        Price as float or None if not found
    """
```

### `src.report` - Report Generation

#### `ReportGenerator`

Handles generation of various report formats.

```python
class ReportGenerator:
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize report generator.
        
        Args:
            output_dir: Output directory for reports
        """
        
    def generate_turbotax_report(self, gains_file: str = None, output_file: str = None) -> str:
        """
        Generate TurboTax-compatible CSV report.
        
        Args:
            gains_file: Path to gains CSV
            output_file: Output file path
            
        Returns:
            Path to generated report
        """
        
    def generate_pdf_summary(self, gains_df: Optional[pd.DataFrame] = None, income: float = 0, output_file: str = None) -> str:
        """
        Generate PDF summary report.
        
        Args:
            gains_df: Gains/losses DataFrame
            income: Total income amount
            output_file: Output file path
            
        Returns:
            Path to generated PDF
        """
```

#### Functions

```python
def generate_turbotax_report(gains_file: str = None, output_file: str = None) -> str:
    """Convenience function to generate TurboTax report."""

def generate_pdf_summary(gains_df: pd.DataFrame = None, income: float = 0, output_file: str = None) -> str:
    """Convenience function to generate PDF summary."""

def generate_all_reports(gains_df: pd.DataFrame = None, income: float = 0, method: str = 'fifo') -> Dict[str, str]:
    """Generate all available report formats."""
```

### `src.config` - Configuration Management

#### `Config`

Configuration manager for the application.

```python
class Config:
    def __init__(self, config_file: str = 'config/app.conf'):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        
    def get(self, section: str, key: str, fallback: Any = None) -> str:
        """Get configuration value."""
        
    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """Get integer configuration value."""
        
    def getfloat(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get float configuration value."""
        
    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get boolean configuration value."""
```

#### Functions

```python
def load_exchange_mappings(config_path: str = 'config/exchanges.yaml') -> Dict[str, Dict[str, str]]:
    """
    Load exchange field mappings from YAML file.
    
    Args:
        config_path: Path to exchanges YAML file
        
    Returns:
        Dictionary of exchange mappings
    """
```

##  Exception Classes

### `src.exceptions` - Custom Exceptions

```python
class CryptoTaxError(Exception):
    """Base exception class for all crypto tax tool errors."""

class DataValidationError(CryptoTaxError):
    """Raised when data validation fails."""

class FileFormatError(CryptoTaxError):
    """Raised when file format is invalid or unsupported."""

class ExchangeNotSupportedError(CryptoTaxError):
    """Raised when an exchange is not supported."""

class PriceFetchError(CryptoTaxError):
    """Raised when price fetching fails."""

class CalculationError(CryptoTaxError):
    """Raised when tax calculations fail."""

class InsufficientInventoryError(CalculationError):
    """Raised when trying to sell more than available inventory."""

class ReportGenerationError(CryptoTaxError):
    """Raised when report generation fails."""

class ConfigurationError(CryptoTaxError):
    """Raised when configuration is invalid or missing."""

class APIError(CryptoTaxError):
    """Raised when external API calls fail."""
```

### Utility Functions

```python
def validate_required_fields(data: Dict[str, Any], required_fields: List[str], context: str = "data") -> None:
    """Validate that required fields are present."""

def safe_float_conversion(value: Any, field_name: str = "value") -> float:
    """Safely convert value to float."""

def safe_date_conversion(value: Any, field_name: str = "date") -> str:
    """Safely convert value to ISO date string."""
```

##  Data Structures

### Standard Transaction Format

```python
{
    "timestamp": "2024-01-01T12:00:00",  # ISO format datetime
    "type": "buy",                       # Transaction type
    "base_asset": "BTC",                 # Cryptocurrency symbol
    "base_amount": 1.0,                  # Amount of base asset
    "quote_asset": "USD",                # Quote currency
    "quote_amount": 50000.0,             # Value in quote currency
    "fee_amount": 25.0,                  # Transaction fee
    "fee_asset": "USD",                  # Fee currency
    "notes": "Market order"              # Additional information
}
```

### Gain/Loss Record

```python
{
    "date": "2024-06-01",                # Sale date
    "asset": "BTC",                      # Asset sold
    "amount": 0.5,                       # Amount sold
    "proceeds": 30000.0,                 # Sale proceeds
    "cost_basis": 25000.0,               # Cost basis
    "gain_loss": 5000.0,                 # Calculated gain/loss
    "short_term": False,                 # True if held < 1 year
    "method": "fifo"                     # Accounting method used
}
```

##  CLI Interface

### Command Structure

```bash
python src/main.py <command> [arguments] [options]
```

### Available Commands

- `auto-process` - Auto-detect and process files
- `detect` - Detect exchange formats
- `normalize` - Convert exchange data
- `calculate` - Calculate taxes
- `report` - Generate reports
- `validate` - Validate data
- `list-exchanges` - Show supported exchanges

### Command Examples

```bash
# Auto-process workflow
python src/main.py auto-process --input-dir input --output-dir output

# Detection
python src/main.py detect --file data.csv --normalize

# Manual normalization
python src/main.py normalize data.csv binance --fetch-prices

# Tax calculation
python src/main.py calculate normalized.csv --method fifo --currency usd

# Report generation
python src/main.py report --turbotax --pdf --detailed
```

##  Testing

### Test Structure

```
tests/
 unit/                    # Unit tests for individual modules
 integration/             # Integration tests for workflows
 fixtures/               # Test data and mock responses
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Run specific test file
pytest tests/unit/test_normalize.py
```

##  Configuration Files

### Exchange Mappings (`config/exchanges.yaml`)

```yaml
exchange_name:
  timestamp: "Column Name"
  type: "Type Column"
  base_asset: "Asset Column"
  base_amount: "Amount Column"
  # ... other mappings
  unique_columns: ["Unique", "Identifier", "Columns"]
  signature_patterns: ["exchange", "specific", "patterns"]
```

### Application Settings (`config/app.conf`)

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

---

For more detailed examples and usage patterns, see the [User Guide](README.md) and [FAQ](faq.md).