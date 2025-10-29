#!/usr/bin/env python3
"""
Quick Start Script for Crypto Tax Tool
Get up and running immediately!
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print(" CRYPTO TAX TOOL - QUICK START")
    print("=" * 60)
    print("Professional-grade cryptocurrency tax calculations")
    print("Completely FREE - No subscriptions, no hidden fees")
    print("Privacy-first - All processing happens on your computer")
    print("=" * 60)

def check_python_version():
    """Check Python version."""
    if sys.version_info < (3, 7):
        print(" Error: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f" Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install all dependencies."""
    print("\n Installing dependencies...")
    
    try:
        # Install requirements
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        
        print(" Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    print("\n Creating directories...")
    
    directories = [
        "data/input",
        "data/output",
        "data/output/reports",
        "data/output/logs",
        "data/samples",
        "uploads",
        "temp",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"    {directory}/")
    
    print(" Directories created successfully")

def create_sample_files():
    """Create sample files for testing."""
    print("\n Creating sample files...")
    
    # Sample transaction data
    sample_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,0.1,USD,4500,4.5,USD,Sample Bitcoin purchase
2024-01-15T00:00:00,sell,BTC,0.05,USD,2500,2.5,USD,Sample Bitcoin sale
2024-02-01T00:00:00,buy,ETH,1.0,USD,3000,3.0,USD,Sample Ethereum purchase
2024-02-15T00:00:00,sell,ETH,0.5,USD,1600,1.6,USD,Sample Ethereum sale
2024-03-01T00:00:00,stake,ETH,0.2,USD,0,0,ETH,Staking rewards
"""
    
    with open("data/samples/sample_transactions.csv", "w") as f:
        f.write(sample_data)
    
    print("    data/samples/sample_transactions.csv")
    
    print(" Sample files created successfully")

def test_imports():
    """Test that all modules can be imported."""
    print("\n Testing imports...")
    
    try:
        import pandas
        import yaml
        import requests
        print("    Core dependencies imported successfully")
        
        # Test basic functionality
        from src.config import load_exchange_mappings
        exchanges = load_exchange_mappings()
        print(f"    Loaded {len(exchanges)} exchange configurations")
        
        print(" All tests passed")
        return True
    except Exception as e:
        print(f" Test failed: {e}")
        return False

def print_usage_instructions():
    """Print usage instructions."""
    print("\n" + "=" * 60)
    print(" SETUP COMPLETE!")
    print("=" * 60)
    
    print("\n QUICK START OPTIONS:")
    
    print("\n1. WEB INTERFACE (Recommended):")
    print("   python simple_web_app.py")
    print("   Then open: http://localhost:5000")
    
    print("\n2. ONE-CLICK PROCESSING:")
    print("   # Put your CSV files in data/input/")
    print("   python simple_auto_processor.py")
    
    print("\n3. COMMAND LINE:")
    print("   python src/main.py --help")
    
    print("\n PROJECT STRUCTURE:")
    print("   - data/input/ - Put your CSV files here")
    print("   - data/output/ - Generated reports appear here")
    print("   - data/samples/ - Sample data for testing")
    
    print("\n PRIVACY & SECURITY:")
    print("   - All processing happens locally on your computer")
    print("   - Your financial data never leaves your device")
    print("   - No tracking, no analytics, no data collection")
    
    print("\n COST:")
    print("   - 100% FREE - no subscriptions, no hidden fees")
    print("   - No limits on transactions or exchanges")
    print("   - No premium features - everything is included")
    
    print("\n SUPPORTED EXCHANGES:")
    print("   - 50+ exchanges including Binance, Coinbase, Kraken, Gemini")
    print("   - DeFi platforms like Uniswap, PancakeSwap, SushiSwap")
    print("   - Hardware wallets like Ledger, Trezor, MetaMask")
    
    print("\n TAX SOFTWARE COMPATIBILITY:")
    print("   - TurboTax, H&R Block, TaxAct, TaxSlayer")
    print("   - Credit Karma Tax, CoinLedger")
    print("   - 6 different formats for maximum compatibility")
    
    print("\n" + "=" * 60)
    print(" PRIVACY FIRST |  100% FREE |  PROFESSIONAL GRADE")
    print("=" * 60)

def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n  Some dependencies failed to install.")
        print("   You can try installing them manually later.")
    
    # Create directories
    create_directories()
    
    # Create sample files
    create_sample_files()
    
    # Test imports
    if test_imports():
        print_usage_instructions()
    else:
        print("\n  Setup completed with warnings.")
        print("   Some features may not work properly.")
        print("   Check the error messages above and try again.")

if __name__ == "__main__":
    main()