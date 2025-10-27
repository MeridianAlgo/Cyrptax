"""Custom exception classes for the crypto tax tool."""

from typing import Optional, Dict, Any, List


class CryptoTaxError(Exception):
    """Base exception class for all crypto tax tool errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class DataValidationError(CryptoTaxError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, validation_errors: Optional[List[str]] = None, 
                 file_path: Optional[str] = None):
        details = {}
        if validation_errors:
            details['validation_errors'] = validation_errors
        if file_path:
            details['file_path'] = file_path
        
        super().__init__(message, details)
        self.validation_errors = validation_errors or []
        self.file_path = file_path


class FileFormatError(CryptoTaxError):
    """Raised when file format is invalid or unsupported."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, 
                 expected_format: Optional[str] = None, 
                 actual_format: Optional[str] = None):
        details = {}
        if file_path:
            details['file_path'] = file_path
        if expected_format:
            details['expected_format'] = expected_format
        if actual_format:
            details['actual_format'] = actual_format
        
        super().__init__(message, details)
        self.file_path = file_path
        self.expected_format = expected_format
        self.actual_format = actual_format


class ExchangeNotSupportedError(CryptoTaxError):
    """Raised when an exchange is not supported."""
    
    def __init__(self, exchange_name: str, supported_exchanges: Optional[List[str]] = None):
        message = f"Exchange '{exchange_name}' is not supported"
        details = {'exchange_name': exchange_name}
        
        if supported_exchanges:
            details['supported_exchanges'] = supported_exchanges
            message += f". Supported exchanges: {', '.join(supported_exchanges)}"
        
        super().__init__(message, details)
        self.exchange_name = exchange_name
        self.supported_exchanges = supported_exchanges or []


class PriceFetchError(CryptoTaxError):
    """Raised when price fetching fails."""
    
    def __init__(self, message: str, asset: Optional[str] = None, 
                 date: Optional[str] = None, api_error: Optional[str] = None):
        details = {}
        if asset:
            details['asset'] = asset
        if date:
            details['date'] = date
        if api_error:
            details['api_error'] = api_error
        
        super().__init__(message, details)
        self.asset = asset
        self.date = date
        self.api_error = api_error


class CalculationError(CryptoTaxError):
    """Raised when tax calculations fail."""
    
    def __init__(self, message: str, transaction_id: Optional[str] = None,
                 asset: Optional[str] = None, calculation_method: Optional[str] = None):
        details = {}
        if transaction_id:
            details['transaction_id'] = transaction_id
        if asset:
            details['asset'] = asset
        if calculation_method:
            details['calculation_method'] = calculation_method
        
        super().__init__(message, details)
        self.transaction_id = transaction_id
        self.asset = asset
        self.calculation_method = calculation_method


class InsufficientInventoryError(CalculationError):
    """Raised when trying to sell more than available inventory."""
    
    def __init__(self, asset: str, requested_amount: float, available_amount: float,
                 transaction_id: Optional[str] = None):
        message = (f"Insufficient {asset} inventory: requested {requested_amount}, "
                  f"available {available_amount}")
        
        super().__init__(
            message, 
            transaction_id=transaction_id, 
            asset=asset
        )
        self.requested_amount = requested_amount
        self.available_amount = available_amount
        
        # Add amounts to details
        self.details.update({
            'requested_amount': requested_amount,
            'available_amount': available_amount
        })


class ReportGenerationError(CryptoTaxError):
    """Raised when report generation fails."""
    
    def __init__(self, message: str, report_type: Optional[str] = None,
                 output_file: Optional[str] = None):
        details = {}
        if report_type:
            details['report_type'] = report_type
        if output_file:
            details['output_file'] = output_file
        
        super().__init__(message, details)
        self.report_type = report_type
        self.output_file = output_file


class ConfigurationError(CryptoTaxError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_file: Optional[str] = None,
                 config_key: Optional[str] = None):
        details = {}
        if config_file:
            details['config_file'] = config_file
        if config_key:
            details['config_key'] = config_key
        
        super().__init__(message, details)
        self.config_file = config_file
        self.config_key = config_key


class APIError(CryptoTaxError):
    """Raised when external API calls fail."""
    
    def __init__(self, message: str, api_name: Optional[str] = None,
                 status_code: Optional[int] = None, response_text: Optional[str] = None):
        details = {}
        if api_name:
            details['api_name'] = api_name
        if status_code:
            details['status_code'] = status_code
        if response_text:
            details['response_text'] = response_text
        
        super().__init__(message, details)
        self.api_name = api_name
        self.status_code = status_code
        self.response_text = response_text


class DataIntegrityError(CryptoTaxError):
    """Raised when data integrity checks fail."""
    
    def __init__(self, message: str, check_type: Optional[str] = None,
                 affected_records: Optional[int] = None):
        details = {}
        if check_type:
            details['check_type'] = check_type
        if affected_records:
            details['affected_records'] = affected_records
        
        super().__init__(message, details)
        self.check_type = check_type
        self.affected_records = affected_records


# Exception handling utilities

def handle_file_error(func):
    """Decorator to handle common file-related errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            raise FileFormatError(f"File not found: {e.filename}", file_path=e.filename)
        except PermissionError as e:
            raise FileFormatError(f"Permission denied: {e.filename}", file_path=e.filename)
        except UnicodeDecodeError as e:
            raise FileFormatError(f"File encoding error: {e}", actual_format="Invalid encoding")
        except Exception as e:
            raise CryptoTaxError(f"Unexpected file error: {e}")
    
    return wrapper


def handle_api_error(func):
    """Decorator to handle API-related errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if hasattr(e, 'response'):
                # HTTP error with response
                raise APIError(
                    f"API request failed: {e}",
                    status_code=getattr(e.response, 'status_code', None),
                    response_text=getattr(e.response, 'text', None)
                )
            else:
                # Other API error
                raise APIError(f"API error: {e}")
    
    return wrapper


def validate_required_fields(data: Dict[str, Any], required_fields: List[str], 
                           context: str = "data") -> None:
    """
    Validate that required fields are present in data.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        context: Context description for error messages
        
    Raises:
        DataValidationError: If required fields are missing
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        raise DataValidationError(
            f"Missing required fields in {context}: {missing_fields}",
            validation_errors=[f"Missing field: {field}" for field in missing_fields]
        )


def safe_float_conversion(value: Any, field_name: str = "value") -> float:
    """
    Safely convert a value to float with proper error handling.
    
    Args:
        value: Value to convert
        field_name: Name of the field for error messages
        
    Returns:
        Float value
        
    Raises:
        DataValidationError: If conversion fails
    """
    if value is None or value == '':
        return 0.0
    
    try:
        return float(value)
    except (ValueError, TypeError) as e:
        raise DataValidationError(
            f"Invalid numeric value for {field_name}: {value}",
            validation_errors=[f"Cannot convert '{value}' to float: {e}"]
        )


def safe_date_conversion(value: Any, field_name: str = "date") -> str:
    """
    Safely convert a value to ISO date string with proper error handling.
    
    Args:
        value: Value to convert
        field_name: Name of the field for error messages
        
    Returns:
        ISO date string
        
    Raises:
        DataValidationError: If conversion fails
    """
    if value is None or value == '':
        raise DataValidationError(
            f"Missing date value for {field_name}",
            validation_errors=[f"Date field '{field_name}' is empty"]
        )
    
    try:
        from dateutil import parser
        parsed_date = parser.parse(str(value))
        return parsed_date.isoformat()
    except (ValueError, TypeError) as e:
        raise DataValidationError(
            f"Invalid date format for {field_name}: {value}",
            validation_errors=[f"Cannot parse date '{value}': {e}"]
        )


class ErrorCollector:
    """Utility class to collect multiple errors before raising."""
    
    def __init__(self, context: str = "operation"):
        self.context = context
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def add_error(self, error: str) -> None:
        """Add an error to the collection."""
        self.errors.append(error)
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the collection."""
        self.warnings.append(warning)
    
    def has_errors(self) -> bool:
        """Check if any errors were collected."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if any warnings were collected."""
        return len(self.warnings) > 0
    
    def raise_if_errors(self) -> None:
        """Raise DataValidationError if any errors were collected."""
        if self.has_errors():
            raise DataValidationError(
                f"Validation failed for {self.context}",
                validation_errors=self.errors
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collected errors and warnings."""
        return {
            'context': self.context,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings
        }