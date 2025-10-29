"""Main CLI application for the crypto tax tool."""

import argparse
import sys
import os
import logging
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from normalize import normalize_csv
    from calculate import calculate_taxes
    from report import generate_all_reports, generate_turbotax_report, generate_pdf_summary
    from validate import validate_df
    from config import config, load_exchange_mappings
    from auto_detect import auto_process_input_folder, interactive_exchange_selection, ExchangeDetector
    import pandas as pd
except ImportError:
    # Try with src prefix if running from parent directory
    from src.normalize import normalize_csv
    from src.calculate import calculate_taxes
    from src.report import generate_all_reports, generate_turbotax_report, generate_pdf_summary
    from src.validate import validate_df
    from src.config import config, load_exchange_mappings
    from src.auto_detect import auto_process_input_folder, interactive_exchange_selection, ExchangeDetector
    import pandas as pd


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else getattr(logging, config.get('app', 'log_level', 'INFO'))
    
    # Create logs directory
    log_dir = config.get('output', 'logs_dir', 'output/logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'crypto_tax_tool.log')),
            logging.StreamHandler(sys.stdout) if verbose else logging.NullHandler()
        ]
    )


def cmd_normalize(args) -> None:
    """Handle normalize command."""
    try:
        print(f"Normalizing {args.input_file} from {args.exchange}...")
        
        normalize_csv(
            input_file=args.input_file,
            exchange=args.exchange,
            output_file=args.output,
            remove_duplicates=args.remove_duplicates,
            fetch_missing_prices=args.fetch_prices,
            sheet_name=args.sheet
        )
        
        print(f"Normalization complete. Output saved to: {args.output}")
        
    except Exception as e:
        print(f"Error during normalization: {e}")
        sys.exit(1)


def cmd_calculate(args) -> None:
    """Handle calculate command."""
    try:
        print(f"Calculating taxes using {args.method.upper()} method...")
        
        gains_df, income = calculate_taxes(
            input_file=args.input_file,
            method=args.method,
            tax_currency=args.currency
        )
        
        # Print summary
        if not gains_df.empty:
            short_term = gains_df[gains_df['short_term']]['gain_loss'].sum()
            long_term = gains_df[~gains_df['short_term']]['gain_loss'].sum()
            
            print(f"\nTax Calculation Results ({args.method.upper()}):")
            print(f"   Short-term gains/losses: ${short_term:,.2f}")
            print(f"   Long-term gains/losses:  ${long_term:,.2f}")
            print(f"   Total gains/losses:      ${short_term + long_term:,.2f}")
        else:
            print("\nNo capital gains/losses calculated")
        
        if income > 0:
            print(f"   Taxable income:          ${income:,.2f}")
        
        print(f"\nCalculation complete. Results saved to output/reports/")
        
    except Exception as e:
        print(f"Error during calculation: {e}")
        sys.exit(1)


def cmd_report(args) -> None:
    """Handle report command."""
    try:
        print("Generating reports...")
        
        # Load existing data
        reports_dir = config.get('output', 'reports_dir', 'output/reports')
        gains_file = os.path.join(reports_dir, 'gains_losses.csv')
        
        gains_df = pd.DataFrame()
        income = 0
        
        if os.path.exists(gains_file):
            gains_df = pd.read_csv(gains_file)
        
        # Load income data
        income_file = os.path.join(reports_dir, 'income_events.csv')
        if os.path.exists(income_file):
            income_df = pd.read_csv(income_file)
            income = income_df['income_amount'].sum() if not income_df.empty else 0
        
        generated_reports = []
        
        # Generate requested reports
        if args.turbotax or args.all:
            turbotax_file = generate_turbotax_report()
            generated_reports.append(f"TurboTax CSV: {turbotax_file}")
        
        if args.pdf or args.all:
            pdf_file = generate_pdf_summary(gains_df, income)
            generated_reports.append(f"PDF Summary: {pdf_file}")
        
        if args.detailed or args.all:
            from report import ReportGenerator
            generator = ReportGenerator()
            detailed_file = generator.generate_detailed_report()
            generated_reports.append(f"Detailed CSV: {detailed_file}")
        
        if args.json or args.all:
            from report import ReportGenerator
            generator = ReportGenerator()
            json_file = generator.generate_summary_json(gains_df, income)
            generated_reports.append(f"JSON Summary: {json_file}")
        
        if not generated_reports:
            print("No report type specified. Use --turbotax, --pdf, --detailed, --json, or --all")
            return
        
        print("\n Reports generated:")
        for report in generated_reports:
            print(f"   {report}")
        
    except Exception as e:
        print(f"Error generating reports: {e}")
        sys.exit(1)


def cmd_validate(args) -> None:
    """Handle validate command."""
    try:
        print(f"Validating {args.input_file}...")
        
        df = pd.read_csv(args.input_file)
        results = validate_df(df)
        
        print(f"\nValidation Results:")
        print(f"   Total transactions: {results['total_transactions']}")
        
        if results['errors']:
            print(f"   Errors found: {len(results['errors'])}")
            for error in results['errors']:
                print(f"     - {error}")
        
        if results['warnings']:
            print(f"   Warnings: {len(results['warnings'])}")
            for warning in results['warnings']:
                print(f"     - {warning}")
        
        if results['duplicates_found'] > 0:
            print(f"   Duplicate transactions: {results['duplicates_found']}")
        
        if results['negative_balances']:
            print(f"   Negative balances detected: {len(results['negative_balances'])}")
        
        if not results['errors'] and not results['warnings']:
            print("   All validations passed")
        
    except Exception as e:
        print(f"Error during validation: {e}")
        sys.exit(1)


def cmd_auto_process(args) -> None:
    """Handle auto-process command."""
    try:
        print(" Auto-processing files in input folder...")
        
        results = auto_process_input_folder(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            interactive=not args.no_interactive
        )
        
        if not results:
            print("No files processed.")
            return
        
        # Summary
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'error']
        
        print(f"\nProcessing Summary:")
        print(f"   Successful: {len(successful)}")
        print(f"   Failed: {len(failed)}")
        
        if successful:
            print(f"\nSuccessfully processed files:")
            for result in successful:
                print(f"   {Path(result['input_file']).name} -> {Path(result['output_file']).name}")
        
        if failed:
            print(f"\nFailed files:")
            for result in failed:
                print(f"   {Path(result['input_file']).name}: {result['error']}")
        
        if successful:
            print(f"\nNext steps:")
            print(f"   1. Review normalized files in {args.output_dir}")
            print(f"   2. Combine files if needed: cat output/*_normalized.csv > combined.csv")
            print(f"   3. Calculate taxes: python src/main.py calculate combined.csv")
            print(f"   4. Generate reports: python src/main.py report --all")
        
    except Exception as e:
        print(f"Error during auto-processing: {e}")
        sys.exit(1)


def cmd_detect(args) -> None:
    """Handle detect command."""
    try:
        if args.file:
            # Detect single file
            exchange = interactive_exchange_selection(args.file)
            print(f"\nSelected exchange: {exchange}")
            
            if args.normalize:
                print(f"Normalizing with {exchange} format...")
                output_file = args.output or f"output/{Path(args.file).stem}_normalized.csv"
                
                normalize_csv(
                    input_file=args.file,
                    exchange=exchange,
                    output_file=output_file,
                    fetch_missing_prices=True,
                    remove_duplicates=True
                )
                
                print(f"Normalized to: {output_file}")
        else:
            # Scan input folder
            detector = ExchangeDetector()
            detections = detector.scan_input_folder(args.input_dir)
            
            if not detections:
                print(f"No CSV or XLSX files found in {args.input_dir}")
                return
            
            print(f"\nDetection Results for {len(detections)} files:\n")
            
            for detection in detections:
                file_name = detection['file_name']
                exchange = detection['detected_exchange']
                confidence = detection['confidence']
                
                status = "PASS" if confidence >= 0.7 else "WARN" if confidence >= 0.4 else "FAIL"
                
                print(f"{status} {file_name}")
                print(f"   Exchange: {exchange}")
                print(f"   Confidence: {confidence:.1%}")
                
                if detection['needs_confirmation']:
                    print(f"   Status: Needs manual confirmation")
                else:
                    print(f"   Status: High confidence detection")
                
                print()
        
    except Exception as e:
        print(f"Error during detection: {e}")
        sys.exit(1)


def cmd_list_exchanges(args) -> None:
    """Handle list-exchanges command."""
    try:
        mappings = load_exchange_mappings()
        
        print("Supported Exchanges:")
        print("=" * 50)
        
        for exchange in sorted(mappings.keys()):
            print(f"   {exchange}")
        
        print(f"\nTotal: {len(mappings)} exchanges supported")
        print("\nTo add a new exchange, edit config/exchanges.yaml")
        
    except Exception as e:
        print(f"Error loading exchange list: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Free Crypto Tax Tool - Privacy-focused cryptocurrency tax calculations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-process all files in input folder (RECOMMENDED)
  python src/main.py auto-process
  
  # Detect exchange format for a specific file
  python src/main.py detect --file data/trades.csv --normalize
  
  # Traditional workflow
  python src/main.py normalize data/binance.csv binance --fetch-prices
  python src/main.py calculate output/normalized.csv --method fifo
  python src/main.py report --all
        """
    )
    
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Normalize command
    norm_parser = subparsers.add_parser('normalize', help='Normalize exchange CSV/XLSX to standard format')
    norm_parser.add_argument('input_file', help='Path to input CSV or XLSX file')
    norm_parser.add_argument('exchange', help='Exchange name (use list-exchanges to see supported)')
    norm_parser.add_argument('--output', '-o', default='output/normalized.csv', 
                           help='Output file path (default: output/normalized.csv)')
    norm_parser.add_argument('--remove-duplicates', action='store_true',
                           help='Remove duplicate transactions')
    norm_parser.add_argument('--fetch-prices', action='store_true',
                           help='Fetch missing price data from CoinGecko')
    norm_parser.add_argument('--sheet', help='Sheet name for XLSX files')
    
    # Calculate command
    calc_parser = subparsers.add_parser('calculate', help='Calculate taxes from normalized data')
    calc_parser.add_argument('input_file', help='Path to normalized CSV file')
    calc_parser.add_argument('--method', '-m', default='fifo', 
                           choices=['fifo', 'lifo', 'hifo', 'average_cost', 'specific_id'],
                           help='Tax calculation method (default: fifo)')
    calc_parser.add_argument('--currency', '-c', default='usd',
                           help='Tax currency (default: usd)')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate tax reports')
    report_parser.add_argument('--turbotax', action='store_true',
                             help='Generate TurboTax-compatible CSV')
    report_parser.add_argument('--pdf', action='store_true',
                             help='Generate PDF summary report')
    report_parser.add_argument('--detailed', action='store_true',
                             help='Generate detailed CSV report')
    report_parser.add_argument('--json', action='store_true',
                             help='Generate JSON summary')
    report_parser.add_argument('--all', action='store_true',
                             help='Generate all report types')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate normalized transaction data')
    validate_parser.add_argument('input_file', help='Path to normalized CSV file')
    
    # Auto-process command
    auto_parser = subparsers.add_parser('auto-process', help='Auto-detect and process files in input folder')
    auto_parser.add_argument('--input-dir', default='input',
                           help='Input directory to scan (default: input)')
    auto_parser.add_argument('--output-dir', default='output',
                           help='Output directory for normalized files (default: output)')
    auto_parser.add_argument('--no-interactive', action='store_true',
                           help='Skip interactive confirmation (use auto-detected exchanges)')
    
    # Detect command
    detect_parser = subparsers.add_parser('detect', help='Detect exchange format for files')
    detect_parser.add_argument('--file', help='Specific file to analyze')
    detect_parser.add_argument('--input-dir', default='input',
                             help='Directory to scan for detection (default: input)')
    detect_parser.add_argument('--normalize', action='store_true',
                             help='Normalize file after detection')
    detect_parser.add_argument('--output', help='Output file for normalization')
    
    # List exchanges command
    list_parser = subparsers.add_parser('list-exchanges', help='List supported exchanges')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Handle commands
    if args.command == 'normalize':
        cmd_normalize(args)
    elif args.command == 'calculate':
        cmd_calculate(args)
    elif args.command == 'report':
        cmd_report(args)
    elif args.command == 'validate':
        cmd_validate(args)
    elif args.command == 'auto-process':
        cmd_auto_process(args)
    elif args.command == 'detect':
        cmd_detect(args)
    elif args.command == 'list-exchanges':
        cmd_list_exchanges(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()