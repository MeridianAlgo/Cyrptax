#!/usr/bin/env python3
"""Basic integration test for the crypto tax tool."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from src.config import config, load_exchange_mappings
        print(" Config module imported successfully")
    except Exception as e:
        print(f" Config import failed: {e}")
        return False
    
    try:
        mappings = load_exchange_mappings()
        print(f" Exchange mappings loaded: {len(mappings)} exchanges")
    except Exception as e:
        print(f" Exchange mappings failed: {e}")
        return False
    
    # Test other imports that don't require external dependencies
    try:
        from src.exceptions import CryptoTaxError, DataValidationError
        print(" Exceptions module imported successfully")
    except Exception as e:
        print(f" Exceptions import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from src.config import config
        
        # Test basic config access
        currency = config.get('app', 'default_currency', 'usd')
        method = config.get('app', 'default_tax_method', 'fifo')
        
        print(f" Default currency: {currency}")
        print(f" Default tax method: {method}")
        
        return True
    except Exception as e:
        print(f" Config test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    
    required_files = [
        'src/__init__.py',
        'src/main.py',
        'src/config.py',
        'src/exceptions.py',
        'config/exchanges.yaml',
        'config/app.conf',
        'requirements.txt',
        'LICENSE',
        'README.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f" {file_path}")
    
    if missing_files:
        print(f" Missing files: {missing_files}")
        return False
    
    return True

def test_sample_data():
    """Test that sample data files exist and are readable."""
    print("\nTesting sample data...")
    
    sample_files = [
        'data/examples/binance_sample.csv',
        'data/examples/coinbase_sample.csv',
        'data/examples/kraken_sample.csv'
    ]
    
    for file_path in sample_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    print(f" {file_path} ({len(lines)} lines)")
            except Exception as e:
                print(f" Error reading {file_path}: {e}")
                return False
        else:
            print(f" Missing sample file: {file_path}")
            return False
    
    return True

def main():
    """Run all tests."""
    print("=== Crypto Tax Tool Basic Integration Test ===\n")
    
    tests = [
        test_file_structure,
        test_imports,
        test_config,
        test_sample_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("Test failed!")
        except Exception as e:
            print(f"Test error: {e}")
    
    print(f"\n=== Test Results: {passed}/{total} passed ===")
    
    if passed == total:
        print(" All basic tests passed! The project structure is correct.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Test normalization: python src/main.py normalize data/examples/binance_sample.csv binance")
        print("3. Run full workflow test")
        return True
    else:
        print(" Some tests failed. Please check the issues above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)