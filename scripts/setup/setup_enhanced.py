#!/usr/bin/env python3
"""
Enhanced setup script for Crypto Tax Tool
Installs dependencies, sets up directories, and provides easy startup options.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print(" CRYPTO TAX TOOL - ENHANCED SETUP")
    print("=" * 60)
    print("Privacy-first cryptocurrency tax calculations")
    print("Supporting 50+ exchanges with modern web interface")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print(" Error: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f" Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n Installing dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Install requirements
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        
        print(" Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Error installing dependencies: {e}")
        print("   Try running: pip install -r requirements.txt")
        return False

def create_directories():
    """Create necessary directories."""
    print("\n Creating directories...")
    
    directories = [
        "input",
        "output",
        "output/logs",
        "output/reports",
        "uploads",
        "templates",
        "static",
        "static/css",
        "static/js",
        "static/images"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"    {directory}/")
    
    print(" Directories created successfully")

def create_sample_files():
    """Create sample configuration and data files."""
    print("\n Creating sample files...")
    
    # Create sample .env file
    env_content = """# Crypto Tax Tool Environment Variables
# Copy this file to .env and fill in your API keys

# Blockchain API Keys (optional)
ETHERSCAN_API_KEY=your_etherscan_api_key_here
BITCOIN_API_KEY=your_bitcoin_api_key_here

# Price API Keys (optional)
COINGECKO_API_KEY=your_coingecko_api_key_here

# Web Interface Settings
FLASK_SECRET_KEY=your_secret_key_here
WEB_HOST=0.0.0.0
WEB_PORT=5000
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    
    print("    .env.example")
    
    # Create sample input files
    sample_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,0.1,USD,4500,4.5,USD,Sample Bitcoin purchase
2024-01-15T00:00:00,sell,BTC,0.05,USD,2500,2.5,USD,Sample Bitcoin sale
2024-02-01T00:00:00,buy,ETH,1.0,USD,3000,3.0,USD,Sample Ethereum purchase
"""
    
    with open("input/sample_transactions.csv", "w") as f:
        f.write(sample_data)
    
    print("    input/sample_transactions.csv")
    
    print(" Sample files created successfully")

def create_startup_scripts():
    """Create convenient startup scripts."""
    print("\n Creating startup scripts...")
    
    # Windows batch file
    if platform.system() == "Windows":
        batch_content = """@echo off
echo Starting Crypto Tax Tool Web Interface...
python web_interface.py
pause
"""
        with open("start_web.bat", "w") as f:
            f.write(batch_content)
        print("    start_web.bat")
    
    # Unix shell script
    shell_content = """#!/bin/bash
echo "Starting Crypto Tax Tool Web Interface..."
python3 web_interface.py
"""
    with open("start_web.sh", "w") as f:
        f.write(shell_content)
    
    # Make executable on Unix systems
    if platform.system() != "Windows":
        os.chmod("start_web.sh", 0o755)
    
    print("    start_web.sh")
    
    # CLI launcher
    cli_content = """#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from main import main
if __name__ == '__main__':
    main()
"""
    with open("crypto_tax_cli.py", "w") as f:
        f.write(cli_content)
    
    if platform.system() != "Windows":
        os.chmod("crypto_tax_cli.py", 0o755)
    
    print("    crypto_tax_cli.py")
    
    print(" Startup scripts created successfully")

def run_tests():
    """Run basic tests to verify installation."""
    print("\n Running basic tests...")
    
    try:
        # Test imports
        import pandas
        import yaml
        import requests
        print("    Core dependencies imported successfully")
        
        # Test basic functionality
        from src.config import load_exchange_mappings
        exchanges = load_exchange_mappings()
        print(f"    Loaded {len(exchanges)} exchange configurations")
        
        print(" Basic tests passed")
        return True
    except Exception as e:
        print(f" Test failed: {e}")
        return False

def print_usage_instructions():
    """Print usage instructions."""
    print("\n" + "=" * 60)
    print(" SETUP COMPLETE!")
    print("=" * 60)
    print("\n USAGE INSTRUCTIONS:")
    print("\n1. WEB INTERFACE (Recommended):")
    if platform.system() == "Windows":
        print("   Double-click: start_web.bat")
    else:
        print("   Run: ./start_web.sh")
    print("   Then open: http://localhost:5000")
    
    print("\n2. COMMAND LINE INTERFACE:")
    print("   Run: python crypto_tax_cli.py --help")
    print("   Or: python src/main.py --help")
    
    print("\n3. QUICK START:")
    print("   # Auto-process files in input/ folder")
    print("   python src/main.py auto-process")
    print("   ")
    print("   # Calculate taxes")
    print("   python src/main.py calculate output/combined_normalized.csv --method fifo")
    print("   ")
    print("   # Generate reports")
    print("   python src/main.py report --all")
    
    print("\n4. SAMPLE DATA:")
    print("   Check input/sample_transactions.csv for example data")
    
    print("\n5. CONFIGURATION:")
    print("   Copy .env.example to .env and add your API keys")
    print("   Edit config/exchanges.yaml to add new exchanges")
    
    print("\n6. SUPPORTED EXCHANGES:")
    print("   Binance, Coinbase, Kraken, Gemini, KuCoin, and 45+ more!")
    
    print("\n" + "=" * 60)
    print(" PRIVACY: All processing happens locally on your computer")
    print(" DOCS: See docs/ directory for detailed documentation")
    print(" ISSUES: Report bugs on GitHub")
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
    
    # Create startup scripts
    create_startup_scripts()
    
    # Run tests
    if run_tests():
        print_usage_instructions()
    else:
        print("\n  Setup completed with warnings.")
        print("   Some features may not work properly.")
        print("   Check the error messages above and try again.")

if __name__ == "__main__":
    main()
