"""Pytest configuration and shared fixtures for the crypto tax tool tests."""

import pytest
import tempfile
import os
import sys
import pandas as pd
from pathlib import Path
import shutil

# Add src to path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_binance_csv():
    """Create a sample Binance CSV file."""
    data = """time,type,base-asset,quantity,quote-asset,total,fee,fee-currency
2024-01-01T00:00:00,buy,BTC,1.0,USDT,50000.0,25.0,USDT
2024-02-01T00:00:00,buy,ETH,10.0,USDT,30000.0,15.0,USDT
2024-06-01T00:00:00,sell,BTC,0.5,USDT,30000.0,15.0,USDT
2024-07-01T00:00:00,sell,ETH,5.0,USDT,20000.0,10.0,USDT"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(data)
        temp_file = f.name
    
    yield temp_file
    os.unlink(temp_file)


@pytest.fixture
def sample_coinbase_csv():
    """Create a sample Coinbase CSV file."""
    data = """Timestamp,Transaction Type,Asset,Quantity Transacted,Spot Price Currency,Subtotal,Fees and/or Spread,Notes
2024-01-01T00:00:00Z,Buy,BTC,0.5,USD,25000.00,50.00,Market order
2024-02-01T00:00:00Z,Buy,ETH,5.0,USD,15000.00,30.00,Market order
2024-06-01T00:00:00Z,Sell,BTC,0.25,USD,13000.00,26.00,Limit order
2024-07-01T00:00:00Z,Sell,ETH,2.5,USD,8000.00,16.00,Limit order"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(data)
        temp_file = f.name
    
    yield temp_file
    os.unlink(temp_file)


@pytest.fixture
def sample_kraken_csv():
    """Create a sample Kraken CSV file."""
    data = """time,type,pair,vol,cost,fee,ledgers
2024-01-01T00:00:00Z,buy,XBTUSD,0.5,25000.00,12.50,L123456
2024-02-01T00:00:00Z,buy,XETHZUSD,5.0,15000.00,7.50,L123457
2024-06-01T00:00:00Z,sell,XBTUSD,0.25,13000.00,6.50,L123458
2024-07-01T00:00:00Z,sell,XETHZUSD,2.5,8000.00,4.00,L123459"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(data)
        temp_file = f.name
    
    yield temp_file
    os.unlink(temp_file)


@pytest.fixture
def sample_normalized_csv():
    """Create a sample normalized CSV file."""
    data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,1.0,USD,50000.0,25.0,USD,
2024-02-01T00:00:00,buy,ETH,10.0,USD,30000.0,15.0,USD,
2024-06-01T00:00:00,sell,BTC,0.5,USD,30000.0,15.0,USD,
2024-07-01T00:00:00,sell,ETH,5.0,USD,20000.0,10.0,USD,"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(data)
        temp_file = f.name
    
    yield temp_file
    os.unlink(temp_file)


@pytest.fixture
def sample_gains_dataframe():
    """Create a sample gains DataFrame for testing reports."""
    data = {
        'asset': ['BTC', 'ETH', 'BTC'],
        'amount': [0.5, 5.0, 0.3],
        'acquisition_date': ['2024-01-01', '2024-02-01', '2024-01-15'],
        'sale_date': ['2024-06-01', '2024-07-01', '2024-08-01'],
        'cost_basis': [25012.5, 15007.5, 15000.0],
        'proceeds': [29985.0, 19990.0, 18000.0],
        'gain_loss': [4972.5, 4982.5, 3000.0],
        'short_term': [True, True, True]
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_income_data():
    """Create sample income data for testing."""
    return [
        {
            'date': '2024-03-01',
            'asset': 'ETH',
            'amount': 1.0,
            'value': 3000.0,
            'type': 'staking'
        },
        {
            'date': '2024-04-01',
            'asset': 'TOKEN',
            'amount': 100.0,
            'value': 500.0,
            'type': 'airdrop'
        }
    ]


@pytest.fixture
def mock_price_data():
    """Mock price data for testing price fetching."""
    return {
        ('BTC', '2024-01-01', 'usd'): 50000.0,
        ('BTC', '2024-06-01', 'usd'): 60000.0,
        ('ETH', '2024-02-01', 'usd'): 3000.0,
        ('ETH', '2024-07-01', 'usd'): 4000.0,
        ('TOKEN', '2024-04-01', 'usd'): 5.0
    }


@pytest.fixture(scope="session")
def test_data_dir():
    """Create a test data directory with sample files."""
    test_dir = tempfile.mkdtemp(prefix="crypto_tax_test_")
    
    # Create subdirectories
    input_dir = os.path.join(test_dir, 'input')
    output_dir = os.path.join(test_dir, 'output')
    os.makedirs(input_dir)
    os.makedirs(output_dir)
    
    # Create sample files
    binance_data = """time,type,base-asset,quantity,quote-asset,total,fee,fee-currency
2024-01-01T00:00:00,buy,BTC,1.0,USDT,50000.0,25.0,USDT
2024-06-01T00:00:00,sell,BTC,0.5,USDT,30000.0,15.0,USDT"""
    
    with open(os.path.join(input_dir, 'binance_sample.csv'), 'w') as f:
        f.write(binance_data)
    
    coinbase_data = """Timestamp,Transaction Type,Asset,Quantity Transacted,Spot Price Currency,Subtotal,Fees and/or Spread,Notes
2024-01-01T00:00:00Z,Buy,BTC,0.5,USD,25000.00,50.00,Market order
2024-06-01T00:00:00Z,Sell,BTC,0.25,USD,13000.00,26.00,Limit order"""
    
    with open(os.path.join(input_dir, 'coinbase_sample.csv'), 'w') as f:
        f.write(coinbase_data)
    
    yield test_dir
    
    # Cleanup
    shutil.rmtree(test_dir)


# Test markers for categorizing tests
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "network: Tests requiring network access")


# Skip network tests by default
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle markers."""
    if config.getoption("--skip-network"):
        skip_network = pytest.mark.skip(reason="--skip-network option given")
        for item in items:
            if "network" in item.keywords:
                item.add_marker(skip_network)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--skip-network",
        action="store_true",
        default=False,
        help="Skip tests that require network access"
    )
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests"
    )


# Custom assertions for financial data
class FinancialAssertions:
    """Custom assertions for financial calculations."""
    
    @staticmethod
    def assert_currency_equal(actual, expected, tolerance=0.01):
        """Assert currency values are equal within tolerance."""
        assert abs(actual - expected) <= tolerance, \
            f"Currency values not equal: {actual} != {expected} (tolerance: {tolerance})"
    
    @staticmethod
    def assert_percentage_equal(actual, expected, tolerance=0.001):
        """Assert percentage values are equal within tolerance."""
        assert abs(actual - expected) <= tolerance, \
            f"Percentage values not equal: {actual} != {expected} (tolerance: {tolerance})"


@pytest.fixture
def financial_assertions():
    """Provide financial assertion helpers."""
    return FinancialAssertions()


# Performance monitoring
@pytest.fixture
def performance_monitor():
    """Monitor test performance."""
    import time
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
        
        def assert_max_time(self, max_seconds):
            assert self.elapsed <= max_seconds, \
                f"Test took too long: {self.elapsed:.2f}s > {max_seconds}s"
    
    return PerformanceMonitor()


# Database fixtures for testing (if needed)
@pytest.fixture
def temp_database():
    """Create a temporary database for testing."""
    import sqlite3
    
    db_file = tempfile.mktemp(suffix='.db')
    conn = sqlite3.connect(db_file)
    
    # Create test tables if needed
    conn.execute('''
        CREATE TABLE IF NOT EXISTS test_transactions (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            type TEXT,
            asset TEXT,
            amount REAL
        )
    ''')
    conn.commit()
    
    yield conn
    
    conn.close()
    if os.path.exists(db_file):
        os.unlink(db_file)


# Logging configuration for tests
@pytest.fixture(autouse=True)
def configure_test_logging():
    """Configure logging for tests."""
    import logging
    
    # Set logging level to WARNING to reduce noise during tests
    logging.getLogger().setLevel(logging.WARNING)
    
    # Disable specific loggers that are too verbose
    logging.getLogger('requests').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.ERROR)


# Environment setup
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    # Set test-specific environment variables
    monkeypatch.setenv('CRYPTO_TAX_TEST_MODE', '1')
    monkeypatch.setenv('CRYPTO_TAX_LOG_LEVEL', 'WARNING')
    
    # Mock external API calls by default
    monkeypatch.setenv('CRYPTO_TAX_MOCK_API', '1')


# Cleanup helpers
@pytest.fixture
def cleanup_files():
    """Track and cleanup test files."""
    files_to_cleanup = []
    
    def add_file(filepath):
        files_to_cleanup.append(filepath)
    
    yield add_file
    
    # Cleanup
    for filepath in files_to_cleanup:
        if os.path.exists(filepath):
            try:
                os.unlink(filepath)
            except OSError:
                pass  # File may already be deleted