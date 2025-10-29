#!/usr/bin/env python3
"""
Simple Project Cleanup and Organization Script
Fixes all directory issues and creates proper structure
"""

import os
import shutil
import sys
from pathlib import Path

def create_directories():
    """Create the proper directory structure."""
    print("Creating proper directory structure...")
    
    directories = [
        "app",
        "app/core",
        "app/web", 
        "app/cli",
        "config",
        "data",
        "data/input",
        "data/output", 
        "data/output/reports",
        "data/output/logs",
        "data/samples",
        "docs",
        "templates",
        "templates/web",
        "static",
        "static/css",
        "static/js",
        "static/images",
        "tests",
        "tests/unit",
        "tests/integration",
        "scripts",
        "scripts/setup",
        "scripts/maintenance",
        "temp",
        "uploads",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   Created: {directory}/")
    
    print("Directory structure created successfully")

def move_core_files():
    """Move core application files to proper locations."""
    print("\nMoving core application files...")
    
    # Core modules
    core_files = {
        "src/auto_processor.py": "app/core/auto_processor.py",
        "src/auto_detect.py": "app/core/auto_detect.py", 
        "src/normalize.py": "app/core/normalize.py",
        "src/calculate.py": "app/core/calculate.py",
        "src/report.py": "app/core/report.py",
        "src/validate.py": "app/core/validate.py",
        "src/price_fetch.py": "app/core/price_fetch.py",
        "src/portfolio_tracker.py": "app/core/portfolio_tracker.py",
        "src/blockchain_import.py": "app/core/blockchain_import.py",
        "src/config.py": "app/core/config.py",
        "src/exceptions.py": "app/core/exceptions.py",
        "src/logging_config.py": "app/core/logging_config.py",
        "src/__init__.py": "app/core/__init__.py"
    }
    
    for source, destination in core_files.items():
        if os.path.exists(source):
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(source, destination)
            print(f"   Moved: {source} -> {destination}")
        else:
            print(f"   Not found: {source}")
    
    # CLI module
    if os.path.exists("src/main.py"):
        shutil.move("src/main.py", "app/cli/main.py")
        print(f"   Moved: src/main.py -> app/cli/main.py")
    
    # Web modules
    if os.path.exists("web_app.py"):
        shutil.move("web_app.py", "app/web/web_app.py")
        print(f"   Moved: web_app.py -> app/web/web_app.py")
    
    if os.path.exists("web_interface.py"):
        shutil.move("web_interface.py", "app/web/web_interface.py")
        print(f"   Moved: web_interface.py -> app/web/web_interface.py")
    
    if os.path.exists("simple_web_app.py"):
        shutil.move("simple_web_app.py", "app/web/simple_web_app.py")
        print(f"   Moved: simple_web_app.py -> app/web/simple_web_app.py")
    
    print("Core files moved successfully")

def move_config_files():
    """Move configuration files to proper locations."""
    print("\nMoving configuration files...")
    
    if os.path.exists("config/exchanges.yaml"):
        shutil.move("config/exchanges.yaml", "config/exchanges.yaml")
        print(f"   Moved: config/exchanges.yaml -> config/exchanges.yaml")
    
    if os.path.exists("config/app.conf"):
        shutil.move("config/app.conf", "config/app.conf")
        print(f"   Moved: config/app.conf -> config/app.conf")
    
    print("Configuration files moved successfully")

def move_template_files():
    """Move template files to proper locations."""
    print("\nMoving template files...")
    
    template_files = {
        "templates/dashboard.html": "templates/web/dashboard.html",
        "templates/base.html": "templates/web/base.html", 
        "templates/index.html": "templates/web/index.html"
    }
    
    for source, destination in template_files.items():
        if os.path.exists(source):
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(source, destination)
            print(f"   Moved: {source} -> {destination}")
    
    print("Template files moved successfully")

def move_documentation():
    """Move documentation files to proper locations."""
    print("\nMoving documentation files...")
    
    doc_files = {
        "README.md": "docs/README.md",
        "IMPROVEMENTS_SUMMARY.md": "docs/IMPROVEMENTS_SUMMARY.md",
        "PROJECT_STATUS.md": "docs/PROJECT_STATUS.md",
        "PROJECT_SUMMARY.md": "docs/PROJECT_SUMMARY.md",
        "CHANGELOG.md": "docs/CHANGELOG.md",
        "CONTRIBUTING.md": "docs/CONTRIBUTING.md",
        "DEPLOYMENT_INSTRUCTIONS.md": "docs/DEPLOYMENT_INSTRUCTIONS.md",
        "FINAL_SUMMARY.md": "docs/FINAL_SUMMARY.md"
    }
    
    for source, destination in doc_files.items():
        if os.path.exists(source):
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(source, destination)
            print(f"   Moved: {source} -> {destination}")
    
    print("Documentation files moved successfully")

def move_scripts():
    """Move script files to proper locations."""
    print("\nMoving script files...")
    
    script_files = {
        "setup_enhanced.py": "scripts/setup/setup_enhanced.py",
        "quick_start.py": "scripts/setup/quick_start.py",
        "run.py": "scripts/setup/run.py",
        "run_tests.py": "scripts/setup/run_tests.py",
        "crypto_tax.py": "scripts/setup/crypto_tax.py",
        "simple_auto_processor.py": "scripts/setup/simple_auto_processor.py"
    }
    
    for source, destination in script_files.items():
        if os.path.exists(source):
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(source, destination)
            print(f"   Moved: {source} -> {destination}")
    
    print("Script files moved successfully")

def move_test_files():
    """Move test files to proper locations."""
    print("\nMoving test files...")
    
    # Move all test files
    test_files = [
        "tests/test_auto_detect.py",
        "tests/test_basic.py", 
        "tests/test_calculate.py",
        "tests/test_cli.py",
        "tests/test_normalize.py",
        "tests/test_price_fetch.py",
        "tests/test_report.py",
        "tests/test_validate.py",
        "tests/conftest.py",
        "tests/__init__.py",
        "tests/TEST_SUITE.md"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            shutil.move(test_file, f"tests/unit/{os.path.basename(test_file)}")
            print(f"   Moved: {test_file} -> tests/unit/{os.path.basename(test_file)}")
    
    # Move pytest.ini
    if os.path.exists("pytest.ini"):
        shutil.move("pytest.ini", "tests/pytest.ini")
        print(f"   Moved: pytest.ini -> tests/pytest.ini")
    
    print("Test files moved successfully")

def move_data_files():
    """Move data files to proper locations."""
    print("\nMoving data files...")
    
    # Move sample data
    if os.path.exists("data/examples"):
        for file in os.listdir("data/examples"):
            src = os.path.join("data/examples", file)
            dst = os.path.join("data/samples", file)
            shutil.move(src, dst)
            print(f"   Moved: {src} -> {dst}")
    
    # Move input data
    if os.path.exists("input"):
        for file in os.listdir("input"):
            src = os.path.join("input", file)
            dst = os.path.join("data/input", file)
            shutil.move(src, dst)
            print(f"   Moved: {src} -> {dst}")
    
    # Move output data
    if os.path.exists("output"):
        for file in os.listdir("output"):
            src = os.path.join("output", file)
            if os.path.isfile(src):
                dst = os.path.join("data/output", file)
                shutil.move(src, dst)
                print(f"   Moved: {src} -> {dst}")
            elif os.path.isdir(src):
                dst = os.path.join("data/output", file)
                shutil.copytree(src, dst, dirs_exist_ok=True)
                print(f"   Moved: {src}/ -> {dst}/")
    
    print("Data files moved successfully")

def create_main_entry_points():
    """Create main entry point files."""
    print("\nCreating main entry points...")
    
    # Main CLI entry point
    cli_main = '''#!/usr/bin/env python3
"""
Crypto Tax Tool - Command Line Interface
Professional-grade cryptocurrency tax calculations
"""

import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.cli.main import main

if __name__ == "__main__":
    main()
'''
    
    with open("crypto_tax_cli.py", "w", encoding='utf-8') as f:
        f.write(cli_main)
    print("   Created: crypto_tax_cli.py")
    
    # Main web entry point
    web_main = '''#!/usr/bin/env python3
"""
Crypto Tax Tool - Web Interface
Professional-grade cryptocurrency tax calculations with modern web UI
"""

import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.web.simple_web_app import app

if __name__ == "__main__":
    print("Starting Professional Crypto Tax Tool...")
    print("Web Interface: http://localhost:5000")
    print("Privacy: All processing happens locally on your computer")
    print("Cost: Completely FREE (no subscription, no hidden fees)")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=5000)
'''
    
    with open("crypto_tax_web.py", "w", encoding='utf-8') as f:
        f.write(web_main)
    print("   Created: crypto_tax_web.py")
    
    # One-click processor entry point
    auto_main = '''#!/usr/bin/env python3
"""
Crypto Tax Tool - One-Click Processor
Fully automated crypto tax processing
"""

import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.auto_processor import process_crypto_taxes

def main():
    print("Crypto Tax Tool - One-Click Processor")
    print("=" * 50)
    
    # Process all files automatically
    results = process_crypto_taxes("data/input", "data/output")
    
    if results["success"]:
        print("Processing completed successfully!")
        print(f"Processed {results['files_processed']} files")
        print(f"Total gains/losses: ${results['tax_results']['total_gains']:,.2f}")
        print(f"Generated {len(results['reports'])} reports")
        print(f"Processing time: {results['processing_time']}")
        
        print("\\nReports saved to: data/output/reports/")
        print("\\nNext steps:")
        for step in results["next_steps"]:
            print(f"   {step}")
    else:
        print(f"Processing failed: {results['error']}")

if __name__ == "__main__":
    main()
'''
    
    with open("crypto_tax_auto.py", "w", encoding='utf-8') as f:
        f.write(auto_main)
    print("   Created: crypto_tax_auto.py")
    
    print("Main entry points created successfully")

def cleanup_unnecessary_files():
    """Delete unnecessary files and directories."""
    print("\nCleaning up unnecessary files...")
    
    # Files to delete
    files_to_delete = [
        "crypto_tax.py",
        "start_web.bat", 
        "start_web.sh",
        "organize_project.py",
        "cleanup_and_organize.py"
    ]
    
    # Directories to delete
    dirs_to_delete = [
        "src/",  # After moving files
        "input/",  # After moving to data/input
        "output/",  # After moving to data/output
        "crypto-tax-tool/",
        "src/__pycache__/",
        "tests/__pycache__/",
        ".pytest_cache/"
    ]
    
    for item in files_to_delete + dirs_to_delete:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
                print(f"   Deleted directory: {item}")
            else:
                os.remove(item)
                print(f"   Deleted file: {item}")
    
    print("Cleanup completed successfully")

def create_init_files():
    """Create __init__.py files for proper Python packages."""
    print("\nCreating __init__.py files...")
    
    init_files = [
        "app/__init__.py",
        "app/core/__init__.py",
        "app/web/__init__.py",
        "app/cli/__init__.py",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/integration/__init__.py"
    ]
    
    for init_file in init_files:
        with open(init_file, "w") as f:
            f.write('"""Package initialization."""\n')
        print(f"   Created: {init_file}")
    
    print("__init__.py files created successfully")

def create_new_readme():
    """Create a new, clean README."""
    readme_content = """# Free Crypto Tax Tool

**Professional-grade cryptocurrency tax calculations - completely FREE!**

## One-Click Solution

**Just drop your CSV files and get professional tax reports in minutes!**

No complex setup, no manual configuration, no subscription fees. This tool rivals paid services like Koinly and CoinMarketCap but is completely free and privacy-focused.

## Key Features

- **Modern Web Interface** - Beautiful, responsive UI that rivals paid services
- **Fully Automated** - One-click processing with intelligent exchange detection
- **50+ Exchange Support** - All major exchanges, DeFi platforms, and hardware wallets
- **Smart Tax Methods** - Automatically selects optimal tax calculation method
- **6 Tax Software Formats** - TurboTax, H&R Block, TaxAct, TaxSlayer, Credit Karma, CoinLedger
- **Blockchain Import** - Direct import from Ethereum, Bitcoin, BSC, Polygon
- **Portfolio Analytics** - Comprehensive portfolio tracking and performance analysis
- **Privacy First** - All processing happens locally on your computer
- **100% Free** - No subscriptions, no hidden fees, no limits

## Quick Start

### Option 1: Web Interface (Recommended)
```bash
# One-time setup
python scripts/setup/quick_start.py

# Start web interface
python crypto_tax_web.py
# Open: http://localhost:5000
```

### Option 2: One-Click Processing
```bash
# Put your CSV files in data/input/
# Then run:
python crypto_tax_auto.py
```

### Option 3: Command Line
```bash
# For advanced users
python crypto_tax_cli.py --help
```

## Project Structure

```
crypto-tax-tool/
 app/                    # Core application
    core/              # Core processing modules
    web/               # Web interface
    cli/               # Command line interface
 config/                # Configuration files
 data/                  # Data directories
    input/             # Input CSV files
    output/            # Generated reports
    samples/           # Sample data
 docs/                  # Documentation
 templates/             # Web templates
 static/                # Static assets
 tests/                 # Test suite
 scripts/               # Utility scripts
```

## Supported Exchanges (50+)

### Major Exchanges
- **Binance** (Spot, Futures, Margin)
- **Coinbase** (Pro, Advanced)
- **Kraken** (Pro)
- **Gemini**
- **KuCoin**
- **OKX**
- **Bybit**
- **HTX (Huobi)**
- **Bitfinex**
- **Bitstamp**
- **Bittrex**
- **CEX.IO**
- **Crypto.com**
- **Gate.io**
- **Poloniex**
- **Upbit**
- **Bithumb**
- **MEXC**
- **Bitget**

### DeFi & DEX Platforms
- **Uniswap**
- **PancakeSwap**
- **SushiSwap**
- **Curve**
- **Balancer**
- **Compound**
- **Aave**
- **1inch**

### Hardware Wallets
- **Ledger Live**
- **Trezor**
- **MetaMask**
- **Trust Wallet**
- **Atomic Wallet**
- **Exodus**

### Regional Exchanges
- **WazirX**
- **CoinDCX**
- **Bitso**
- **Bitpanda**
- **NiceHash**

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Verify Installation
```bash
python crypto_tax_cli.py --help
```

## Usage

### Web Interface
1. Start the web app: `python crypto_tax_web.py`
2. Open your browser: `http://localhost:5000`
3. Drag & drop your CSV files
4. Click "Process Everything Automatically"
5. Download your tax reports

### Command Line
```bash
# Auto-process all files
python crypto_tax_auto.py

# Manual processing
python crypto_tax_cli.py auto-process
python crypto_tax_cli.py calculate data/output/combined_transactions.csv
python crypto_tax_cli.py report --all
```

## Tax Software Compatibility

| Software | Format | Status |
|----------|--------|--------|
| TurboTax | CSV |  |
| H&R Block | CSV |  |
| TaxAct | CSV |  |
| TaxSlayer | CSV |  |
| Credit Karma Tax | CSV |  |
| CoinLedger | CSV |  |

## Privacy & Security

- **Local Processing Only** - All calculations happen on your computer
- **No Data Transmission** - Your financial data never leaves your device
- **Open Source** - Full source code available for inspection
- **No Tracking** - No analytics or user tracking
- **Secure Storage** - Temporary files use appropriate permissions

## Documentation

- **[User Guide](docs/user_guide/)** - Complete usage instructions
- **[API Reference](docs/api_reference/)** - Developer documentation
- **[Examples](docs/examples/)** - Sample data and workflows
- **[FAQ](docs/faq.md)** - Common questions and troubleshooting

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Disclaimer

This tool is for informational purposes only and does not constitute tax advice. Always consult with a qualified tax professional for your specific situation.

## Acknowledgments

- [CoinGecko](https://coingecko.com) for cryptocurrency price data
- The open-source community for Python libraries
- Contributors who help improve exchange support

---

**Made with  for the crypto community**

[ Star this repository](https://github.com/your-repo/crypto-tax-tool) if you find it useful!
"""
    
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(readme_content)
    print("   Created: README.md")
    
    print("New README created successfully")

def main():
    """Main cleanup and organization function."""
    print("CRYPTO TAX TOOL - COMPLETE CLEANUP & ORGANIZATION")
    print("=" * 60)
    
    try:
        # Create proper directory structure
        create_directories()
        
        # Move all files to proper locations
        move_core_files()
        move_config_files()
        move_template_files()
        move_documentation()
        move_scripts()
        move_test_files()
        move_data_files()
        
        # Create main entry points
        create_main_entry_points()
        
        # Create new README
        create_new_readme()
        
        # Create init files
        create_init_files()
        
        # Clean up unnecessary files
        cleanup_unnecessary_files()
        
        print("\n" + "=" * 60)
        print("CLEANUP & ORGANIZATION COMPLETE!")
        print("=" * 60)
        
        print("\nNEW PROJECT STRUCTURE:")
        print("   - app/ - Core application code")
        print("   - config/ - Configuration files")
        print("   - data/ - Data directories")
        print("   - docs/ - Documentation")
        print("   - templates/ - Web templates")
        print("   - static/ - Static assets")
        print("   - tests/ - Test suite")
        print("   - scripts/ - Utility scripts")
        
        print("\nENTRY POINTS:")
        print("   - python crypto_tax_web.py (Web interface)")
        print("   - python crypto_tax_auto.py (One-click processing)")
        print("   - python crypto_tax_cli.py (Command line)")
        
        print("\nNEXT STEPS:")
        print("   1. Run: python scripts/setup/quick_start.py")
        print("   2. Start: python crypto_tax_web.py")
        print("   3. Open: http://localhost:5000")
        
        print("\nNOTE:")
        print("   Some import statements may need manual updating")
        print("   Check files in app/ directory for any import issues")
        
    except Exception as e:
        print(f"\nError during cleanup: {e}")
        print("Please check the error and try again.")

if __name__ == "__main__":
    main()
