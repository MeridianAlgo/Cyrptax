#!/usr/bin/env python3
"""Quick start script for the crypto tax tool with auto-detection."""

import os
import sys
from pathlib import Path

def main():
    """Run the complete workflow with auto-detection."""
    
    print("Crypto Tax Tool - Quick Start")
    print("=" * 50)
    
    # Check if input directory exists and has files
    input_dir = Path("input")
    if not input_dir.exists():
        print("Creating input directory...")
        input_dir.mkdir(exist_ok=True)
    
    # Check for files in input directory
    csv_files = list(input_dir.glob("*.csv"))
    xlsx_files = list(input_dir.glob("*.xlsx"))
    all_files = csv_files + xlsx_files
    
    if not all_files:
        print(f"\nNo CSV or XLSX files found in the input/ directory.")
        print(f"   Please place your exchange export files in the input/ folder.")
        print(f"   Supported formats: CSV, XLSX")
        print(f"\nExample files you can add:")
        print(f"   - binance_trades.csv")
        print(f"   - coinbase_transactions.csv") 
        print(f"   - kraken_ledgers.csv")
        print(f"\n   Then run this script again!")
        return
    
    print(f"\nFound {len(all_files)} files to process:")
    for file in all_files:
        print(f"   - {file.name}")
    
    # Ask user if they want to proceed
    proceed = input(f"\nProcess these files with auto-detection? (y/n): ").strip().lower()
    
    if proceed not in ['y', 'yes']:
        print("Cancelled. Run again when ready!")
        return
    
    print(f"\nStarting auto-processing workflow...")
    print(f"   This will:")
    print(f"   1. Auto-detect exchange formats")
    print(f"   2. Ask for confirmation if confidence is low")
    print(f"   3. Normalize all files to standard format")
    print(f"   4. Fetch missing prices from CoinGecko")
    print(f"   5. Remove duplicate transactions")
    
    # Run auto-processing
    print(f"\n" + "="*50)
    os.system("python src/main.py auto-process")
    
    # Check if any files were processed successfully
    output_dir = Path("output")
    normalized_files = list(output_dir.glob("*_normalized.csv"))
    
    if normalized_files:
        print(f"\nAuto-processing complete!")
        print(f"   Generated {len(normalized_files)} normalized files")
        
        # Ask if user wants to continue with tax calculations
        continue_calc = input(f"\nContinue with tax calculations? (y/n): ").strip().lower()
        
        if continue_calc in ['y', 'yes']:
            # Combine files if multiple
            if len(normalized_files) > 1:
                print(f"\nCombining {len(normalized_files)} normalized files...")
                combined_file = "output/combined_normalized.csv"
                
                # Simple file combination (in production, should handle headers properly)
                with open(combined_file, 'w') as outfile:
                    header_written = False
                    for file in normalized_files:
                        with open(file, 'r') as infile:
                            lines = infile.readlines()
                            if not header_written:
                                outfile.writelines(lines)
                                header_written = True
                            else:
                                outfile.writelines(lines[1:])  # Skip header
                
                input_file = combined_file
                print(f"   ✅ Combined file: {combined_file}")
            else:
                input_file = str(normalized_files[0])
            
            # Calculate taxes
            print(f"\nCalculating taxes using FIFO method...")
            os.system(f"python src/main.py calculate {input_file} --method fifo")
            
            # Generate reports
            print(f"\nGenerating reports...")
            os.system("python src/main.py report --all")
            
            print(f"\nComplete workflow finished!")
            print(f"   Check the output/reports/ directory for your tax reports:")
            print(f"   - turbotax_import.csv (for TurboTax)")
            print(f"   - tax_summary.pdf (human-readable summary)")
            print(f"   - detailed_tax_report.csv (complete details)")
        
        else:
            print(f"\nFiles normalized successfully!")
            print(f"   Next steps:")
            print(f"   1. Review normalized files in output/ directory")
            print(f"   2. Run: python src/main.py calculate output/combined.csv")
            print(f"   3. Run: python src/main.py report --all")
    
    else:
        print(f"\nNo files were processed successfully.")
        print(f"   Check the error messages above and try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\nCancelled by user")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)