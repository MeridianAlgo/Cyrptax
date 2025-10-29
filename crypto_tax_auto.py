#!/usr/bin/env python3
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
        
        print("\nReports saved to: data/output/reports/")
        print("\nNext steps:")
        for step in results["next_steps"]:
            print(f"   {step}")
    else:
        print(f"Processing failed: {results['error']}")

if __name__ == "__main__":
    main()
