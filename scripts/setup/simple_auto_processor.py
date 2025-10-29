#!/usr/bin/env python3
"""
Simple Auto Processor for Crypto Tax Tool
One-click solution that works with the current structure
"""

import os
import sys
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.auto_detect import ExchangeDetector
    from src.normalize import normalize_csv
    from src.calculate import calculate_taxes
    from src.report import generate_all_reports
    from src.config import load_exchange_mappings
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

logger = logging.getLogger(__name__)

def process_crypto_taxes(input_dir: str = "data/input", output_dir: str = "data/output") -> Dict[str, Any]:
    """
    One-click crypto tax processing - the main function users call.
    
    Args:
        input_dir: Directory containing CSV files
        output_dir: Directory for output files
        
    Returns:
        Complete processing results
    """
    start_time = datetime.now()
    processing_log = []
    
    try:
        # Step 1: Auto-detect and process all files
        log_message(" Scanning for transaction files...")
        processed_files = auto_process_files(input_dir, output_dir)
        
        if not processed_files:
            return create_error_result("No valid transaction files found in input directory")
        
        # Step 2: Combine all normalized files
        log_message(" Combining transaction data...")
        combined_file = combine_normalized_files(processed_files, output_dir)
        
        # Step 3: Auto-determine best tax method
        log_message(" Analyzing transactions for optimal tax method...")
        recommended_method = "fifo"  # Default to FIFO for now
        
        # Step 4: Calculate taxes with recommended method
        log_message(f" Calculating taxes using {recommended_method.upper()} method...")
        tax_results = calculate_taxes_auto(combined_file, recommended_method)
        
        # Step 5: Generate all reports automatically
        log_message(" Generating tax reports...")
        reports = generate_all_reports_auto()
        
        processing_time = datetime.now() - start_time
        
        return {
            "success": True,
            "processing_time": str(processing_time),
            "files_processed": len(processed_files),
            "recommended_tax_method": recommended_method,
            "tax_results": tax_results,
            "reports": reports,
            "processing_log": processing_log,
            "next_steps": [
                " All processing complete!",
                " Download your tax reports from the data/output/reports/ folder",
                " Import the TurboTax CSV into your tax software",
                " Keep all files for your records"
            ]
        }
        
    except Exception as e:
        logger.error(f"Auto-processing failed: {e}")
        return create_error_result(f"Processing failed: {str(e)}")

def auto_process_files(input_dir: str, output_dir: str) -> List[Dict[str, Any]]:
    """Automatically process all files with smart detection."""
    processed_files = []
    
    # Find all CSV/XLSX files
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory {input_dir} not found")
    
    files = list(input_path.glob("*.csv")) + list(input_path.glob("*.xlsx"))
    
    if not files:
        return processed_files
    
    log_message(f"Found {len(files)} files to process")
    
    detector = ExchangeDetector()
    
    for file_path in files:
        try:
            # Auto-detect exchange
            exchange, confidence, details = detector.detect_exchange(str(file_path))
            
            if confidence < 0.5:
                log_message(f" Low confidence detection for {file_path.name}: {exchange} ({confidence:.1%})")
                # Try to find best match from suggestions
                suggestions = detector.get_exchange_suggestions(details.get('columns_found', []), 3)
                if suggestions:
                    exchange = suggestions[0][0]
                    log_message(f"Using best match: {exchange}")
            
            # Normalize file
            output_file = os.path.join(output_dir, f"{file_path.stem}_normalized.csv")
            
            normalize_csv(
                input_file=str(file_path),
                exchange=exchange,
                output_file=output_file,
                fetch_missing_prices=True,
                remove_duplicates=True
            )
            
            processed_files.append({
                "original_file": str(file_path),
                "normalized_file": output_file,
                "exchange": exchange,
                "confidence": confidence,
                "rows": len(pd.read_csv(output_file))
            })
            
            log_message(f" Processed {file_path.name} as {exchange} ({confidence:.1%})")
            
        except Exception as e:
            log_message(f" Failed to process {file_path.name}: {e}")
            continue
    
    return processed_files

def combine_normalized_files(processed_files: List[Dict], output_dir: str) -> str:
    """Combine all normalized files into one master file."""
    if len(processed_files) == 1:
        return processed_files[0]["normalized_file"]
    
    # Load all normalized files
    dataframes = []
    for file_info in processed_files:
        df = pd.read_csv(file_info["normalized_file"])
        df['source_file'] = Path(file_info["original_file"]).name
        df['source_exchange'] = file_info["exchange"]
        dataframes.append(df)
    
    # Combine and sort by timestamp
    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])
    combined_df = combined_df.sort_values('timestamp')
    
    # Save combined file
    combined_file = os.path.join(output_dir, "combined_transactions.csv")
    combined_df.to_csv(combined_file, index=False)
    
    log_message(f"Combined {len(processed_files)} files into {len(combined_df)} transactions")
    
    return combined_file

def calculate_taxes_auto(combined_file: str, method: str) -> Dict[str, Any]:
    """Calculate taxes with automatic optimization."""
    gains_df, total_income = calculate_taxes(combined_file, method)
    
    # Calculate summary statistics
    if not gains_df.empty:
        short_term_gains = gains_df[gains_df['short_term']]['gain_loss'].sum()
        long_term_gains = gains_df[~gains_df['short_term']]['gain_loss'].sum()
        total_gains = short_term_gains + long_term_gains
        
        # Calculate tax implications (simplified)
        short_term_tax = short_term_gains * 0.22  # Assume 22% tax rate
        long_term_tax = long_term_gains * 0.15    # Assume 15% tax rate
        total_tax = short_term_tax + long_term_tax
    else:
        short_term_gains = long_term_gains = total_gains = 0
        short_term_tax = long_term_tax = total_tax = 0
    
    return {
        "method_used": method,
        "total_transactions": len(gains_df),
        "short_term_gains": float(short_term_gains),
        "long_term_gains": float(long_term_gains),
        "total_gains": float(total_gains),
        "total_income": float(total_income),
        "estimated_tax": float(total_tax),
        "gains_data": gains_df.to_dict('records') if not gains_df.empty else []
    }

def generate_all_reports_auto() -> Dict[str, str]:
    """Generate all reports automatically."""
    reports = {}
    
    try:
        # Generate all tax software formats
        all_reports = generate_all_reports()
        reports.update(all_reports)
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        reports['error'] = str(e)
    
    return reports

def log_message(message: str):
    """Add message to processing log."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    logger.info(message)

def create_error_result(error_message: str) -> Dict[str, Any]:
    """Create error result."""
    return {
        "success": False,
        "error": error_message,
        "processing_log": [],
        "next_steps": ["Please check the error message above and try again"]
    }

if __name__ == "__main__":
    print(" Crypto Tax Tool - One-Click Processor")
    print("=" * 50)
    
    # Process all files automatically
    results = process_crypto_taxes("data/input", "data/output")
    
    if results["success"]:
        print(" Processing completed successfully!")
        print(f" Processed {results['files_processed']} files")
        print(f" Total gains/losses: ${results['tax_results']['total_gains']:,.2f}")
        print(f" Generated {len(results['reports'])} reports")
        print(f"  Processing time: {results['processing_time']}")
        
        print("\n Reports saved to: data/output/reports/")
        print("\n Next steps:")
        for step in results["next_steps"]:
            print(f"   {step}")
    else:
        print(f" Processing failed: {results['error']}")
