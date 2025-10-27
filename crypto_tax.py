#!/usr/bin/env python3
"""Standalone crypto tax tool runner."""

import sys
import os
import pandas as pd
from pathlib import Path
import yaml
import logging
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_exchange_mappings(config_path: str = 'config/exchanges.yaml') -> Dict[str, Dict[str, str]]:
    """Load exchange field mappings from YAML file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Exchange mappings file not found: {config_path}")

def detect_exchange(file_path: str) -> Tuple[str, float]:
    """Simple exchange detection based on column headers."""
    try:
        # Read first few rows to analyze headers
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path, nrows=5)
        else:
            df = pd.read_csv(file_path, nrows=5)
        
        columns = [col.lower().strip() for col in df.columns]
        
        # Simple detection logic
        if 'base-asset' in columns and 'quote-asset' in columns:
            return 'binance', 1.0
        elif 'quantity transacted' in columns and 'spot price currency' in columns:
            return 'coinbase', 1.0
        elif 'pair' in columns and 'vol' in columns and 'ledgers' in columns:
            return 'kraken', 1.0
        else:
            # Default to binance if uncertain
            return 'binance', 0.5
            
    except Exception as e:
        logger.error(f"Error detecting exchange: {e}")
        return 'binance', 0.5

def auto_process_files():
    """Auto-process files in input directory."""
    input_dir = Path("input")
    
    if not input_dir.exists():
        print("Creating input directory...")
        input_dir.mkdir(exist_ok=True)
        print("Please place your CSV files in the input/ directory and run again.")
        return
    
    # Find CSV files
    csv_files = list(input_dir.glob("*.csv"))
    xlsx_files = list(input_dir.glob("*.xlsx"))
    all_files = csv_files + xlsx_files
    
    if not all_files:
        print("No CSV or XLSX files found in input/ directory.")
        print("Please place your exchange export files there and run again.")
        return
    
    print(f"Found {len(all_files)} files to process:")
    for file in all_files:
        print(f"  - {file.name}")
    
    # Process each file
    for file_path in all_files:
        print(f"\nProcessing: {file_path.name}")
        
        # Detect exchange
        exchange, confidence = detect_exchange(str(file_path))
        print(f"  Detected exchange: {exchange} (confidence: {confidence:.1%})")
        
        if confidence < 0.8:
            print("  Low confidence detection - you may want to specify the exchange manually")
        
        # For demo purposes, just show what would be done
        print(f"  Would normalize {file_path.name} using {exchange} format")
        print(f"  Would save to: output/{file_path.stem}_normalized.csv")
    
    print(f"\nDemo complete! To run the full implementation:")
    print(f"1. Install dependencies: python -m pip install -r requirements.txt")
    print(f"2. Run: python src/main.py auto-process")

def main():
    """Main entry point."""
    print("Crypto Tax Tool - Demo Runner")
    print("=" * 40)
    
    try:
        auto_process_files()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())