"""Logging configuration for the crypto tax tool."""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.config import config


class CryptoTaxFormatter(logging.Formatter):
    """Custom formatter for crypto tax tool logs."""
    
    def __init__(self):
        super().__init__()
        self.default_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.error_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    
    def format(self, record):
        if record.levelno >= logging.ERROR:
            self._style._fmt = self.error_format
        else:
            self._style._fmt = self.default_format
        
        return super().format(record)


def setup_logging(
    log_level: Optional[str] = None,
    log_to_file: bool = True,
    log_to_console: bool = False,
    verbose: bool = False
) -> None:
    """
    Set up comprehensive logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        verbose: Enable verbose console logging
    """
    # Determine log level
    if log_level is None:
        log_level = config.get('app', 'log_level', 'INFO')
    
    if verbose:
        log_level = 'DEBUG'
        log_to_console = True
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logs directory
    log_dir = Path(config.get('output', 'logs_dir', 'output/logs'))
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set root logger level
    root_logger.setLevel(numeric_level)
    
    # Create formatter
    formatter = CryptoTaxFormatter()
    
    # File handler with rotation
    if log_to_file:
        log_file = log_dir / 'crypto_tax_tool.log'
        
        # Use rotating file handler to prevent huge log files
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Also create a daily log file for easier tracking
        daily_log_file = log_dir / f'crypto_tax_{datetime.now().strftime("%Y%m%d")}.log'
        daily_handler = logging.FileHandler(daily_log_file, encoding='utf-8')
        daily_handler.setLevel(numeric_level)
        daily_handler.setFormatter(formatter)
        root_logger.addHandler(daily_handler)
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        
        # Use simpler format for console
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Set up specific loggers for different modules
    _setup_module_loggers(numeric_level)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_to_file}, Console: {log_to_console}")


def _setup_module_loggers(level: int) -> None:
    """Set up loggers for specific modules with appropriate levels."""
    
    # Main application modules
    app_modules = [
        'src.main',
        'src.normalize',
        'src.calculate',
        'src.validate',
        'src.report',
        'src.price_fetch',
        'src.config'
    ]
    
    for module in app_modules:
        logger = logging.getLogger(module)
        logger.setLevel(level)
    
    # External libraries - set to WARNING to reduce noise
    external_modules = [
        'requests',
        'urllib3',
        'pandas',
        'openpyxl'
    ]
    
    for module in external_modules:
        logger = logging.getLogger(module)
        logger.setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_function_call(func):
    """
    Decorator to log function calls with parameters and execution time.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        # Log function entry
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.debug(f"{func.__name__} completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    
    return wrapper


def log_performance(operation: str, start_time: datetime, 
                   records_processed: Optional[int] = None) -> None:
    """
    Log performance metrics for operations.
    
    Args:
        operation: Name of the operation
        start_time: When the operation started
        records_processed: Number of records processed (optional)
    """
    logger = logging.getLogger('performance')
    
    execution_time = (datetime.now() - start_time).total_seconds()
    
    if records_processed:
        rate = records_processed / execution_time if execution_time > 0 else 0
        logger.info(f"{operation} completed: {records_processed} records in {execution_time:.2f}s ({rate:.1f} records/sec)")
    else:
        logger.info(f"{operation} completed in {execution_time:.2f}s")


def log_memory_usage(operation: str) -> None:
    """
    Log current memory usage for an operation.
    
    Args:
        operation: Name of the operation
    """
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        logger = logging.getLogger('performance')
        logger.debug(f"{operation} - Memory usage: {memory_mb:.1f} MB")
        
    except ImportError:
        # psutil not available, skip memory logging
        pass


class LoggingContext:
    """Context manager for temporary logging configuration."""
    
    def __init__(self, level: str, module: Optional[str] = None):
        self.level = getattr(logging, level.upper())
        self.module = module
        self.original_levels = {}
    
    def __enter__(self):
        if self.module:
            logger = logging.getLogger(self.module)
            self.original_levels[self.module] = logger.level
            logger.setLevel(self.level)
        else:
            # Change root logger level
            root_logger = logging.getLogger()
            self.original_levels['root'] = root_logger.level
            root_logger.setLevel(self.level)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original levels
        for module, level in self.original_levels.items():
            if module == 'root':
                logging.getLogger().setLevel(level)
            else:
                logging.getLogger(module).setLevel(level)


def create_operation_logger(operation_name: str) -> logging.Logger:
    """
    Create a dedicated logger for a specific operation.
    
    Args:
        operation_name: Name of the operation
        
    Returns:
        Logger instance for the operation
    """
    logger = logging.getLogger(f'operation.{operation_name}')
    
    # Create operation-specific log file
    log_dir = Path(config.get('output', 'logs_dir', 'output/logs'))
    log_file = log_dir / f'{operation_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    # Add file handler for this operation
    handler = logging.FileHandler(log_file, encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    return logger


# Convenience functions for common logging patterns
def log_data_summary(logger: logging.Logger, df, operation: str) -> None:
    """Log summary information about a DataFrame."""
    logger.info(f"{operation} - Processed {len(df)} rows")
    if hasattr(df, 'columns'):
        logger.debug(f"{operation} - Columns: {list(df.columns)}")
    
    # Log data quality metrics
    if len(df) > 0:
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            logger.warning(f"{operation} - Null values found: {null_counts[null_counts > 0].to_dict()}")


def log_validation_results(logger: logging.Logger, results: dict) -> None:
    """Log validation results in a structured format."""
    logger.info(f"Validation completed - {results['total_transactions']} transactions processed")
    
    if results['errors']:
        logger.error(f"Validation errors ({len(results['errors'])}): {results['errors']}")
    
    if results['warnings']:
        logger.warning(f"Validation warnings ({len(results['warnings'])}): {results['warnings']}")
    
    if results['duplicates_found'] > 0:
        logger.warning(f"Duplicate transactions found: {results['duplicates_found']}")
    
    if results['negative_balances']:
        logger.warning(f"Negative balances detected: {len(results['negative_balances'])}")


def log_calculation_summary(logger: logging.Logger, gains_df, income: float, method: str) -> None:
    """Log tax calculation summary."""
    if not gains_df.empty:
        short_term = gains_df[gains_df['short_term']]['gain_loss'].sum()
        long_term = gains_df[~gains_df['short_term']]['gain_loss'].sum()
        total_gains = short_term + long_term
        
        logger.info(f"Tax calculation completed using {method.upper()} method:")
        logger.info(f"  Short-term gains/losses: ${short_term:,.2f}")
        logger.info(f"  Long-term gains/losses: ${long_term:,.2f}")
        logger.info(f"  Total gains/losses: ${total_gains:,.2f}")
        logger.info(f"  Total transactions: {len(gains_df)}")
    else:
        logger.info("No capital gains/losses calculated")
    
    if income > 0:
        logger.info(f"  Total income: ${income:,.2f}")


# Initialize logging when module is imported
def init_default_logging():
    """Initialize default logging configuration."""
    try:
        setup_logging(log_to_console=False, log_to_file=True)
    except Exception as e:
        # Fallback to basic logging if setup fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging.getLogger(__name__).warning(f"Failed to setup advanced logging: {e}")


# Auto-initialize when imported
init_default_logging()