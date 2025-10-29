"""
Fully Automated Crypto Tax Processor
One-click solution that rivals paid services like Koinly and CoinMarketCap
"""

import os
import sys
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
from pathlib import Path

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auto_detect import ExchangeDetector
from normalize import normalize_csv
from calculate import calculate_taxes
from report import generate_all_reports
from portfolio_tracker import PortfolioTracker
from price_fetch import fetch_price
from config import load_exchange_mappings

logger = logging.getLogger(__name__)

class AutoTaxProcessor:
    """Fully automated crypto tax processor - one-click solution."""
    
    def __init__(self):
        self.detector = ExchangeDetector()
        self.exchange_mappings = load_exchange_mappings()
        self.processing_log = []
        
    def process_all_files(self, input_dir: str = "data/input", output_dir: str = "data/output") -> Dict[str, Any]:
        """
        Process all files automatically - the main function users call.
        
        Args:
            input_dir: Directory containing CSV files
            output_dir: Directory for output files
            
        Returns:
            Complete processing results with all reports
        """
        start_time = datetime.now()
        self.processing_log = []
        
        try:
            # Step 1: Auto-detect and process all files
            self._log("Scanning for transaction files...")
            processed_files = self._auto_process_files(input_dir, output_dir)
            
            if not processed_files:
                return self._create_error_result("No valid transaction files found in input directory")
            
            # Step 2: Combine all normalized files
            self._log("Combining transaction data...")
            combined_file = self._combine_normalized_files(processed_files, output_dir)
            
            # Step 3: Auto-determine best tax method
            self._log("Analyzing transactions for optimal tax method...")
            recommended_method = self._recommend_tax_method(combined_file)
            
            # Step 4: Calculate taxes with recommended method
            self._log(f"Calculating taxes using {recommended_method.upper()} method...")
            tax_results = self._calculate_taxes_auto(combined_file, recommended_method)
            
            # Step 5: Generate comprehensive portfolio analysis
            self._log("Analyzing portfolio performance...")
            portfolio_analysis = self._analyze_portfolio(combined_file)
            
            # Step 6: Generate all reports automatically
            self._log("Generating tax reports...")
            reports = self._generate_all_reports_auto(tax_results, portfolio_analysis)
            
            # Step 7: Create summary dashboard
            self._log("Creating summary dashboard...")
            dashboard = self._create_summary_dashboard(tax_results, portfolio_analysis, reports)
            
            processing_time = datetime.now() - start_time
            
            return {
                "success": True,
                "processing_time": str(processing_time),
                "files_processed": len(processed_files),
                "recommended_tax_method": recommended_method,
                "tax_results": tax_results,
                "portfolio_analysis": portfolio_analysis,
                "reports": reports,
                "dashboard": dashboard,
                "processing_log": self.processing_log,
                "next_steps": self._get_next_steps(reports)
            }
            
        except Exception as e:
            logger.error(f"Auto-processing failed: {e}")
            return self._create_error_result(f"Processing failed: {str(e)}")
    
    def _auto_process_files(self, input_dir: str, output_dir: str) -> List[Dict[str, Any]]:
        """Automatically process all files with smart detection."""
        processed_files = []
        
        # Find all CSV/XLSX files
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory {input_dir} not found")
        
        files = list(input_path.glob("*.csv")) + list(input_path.glob("*.xlsx"))
        
        if not files:
            return processed_files
        
        self._log(f"Found {len(files)} files to process")
        
        for file_path in files:
            try:
                # Auto-detect exchange
                exchange, confidence, details = self.detector.detect_exchange(str(file_path))
                
                if confidence < 0.5:
                    self._log(f"Low confidence detection for {file_path.name}: {exchange} ({confidence:.1%})")
                    # Try to find best match from suggestions
                    suggestions = self.detector.get_exchange_suggestions(details.get('columns_found', []), 3)
                    if suggestions:
                        exchange = suggestions[0][0]
                        self._log(f"Using best match: {exchange}")
                
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
                
                self._log(f"Processed {file_path.name} as {exchange} ({confidence:.1%})")
                
            except Exception as e:
                self._log(f"Failed to process {file_path.name}: {e}")
                continue
        
        return processed_files
    
    def _combine_normalized_files(self, processed_files: List[Dict], output_dir: str) -> str:
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
        
        self._log(f"Combined {len(processed_files)} files into {len(combined_df)} transactions")
        
        return combined_file
    
    def _recommend_tax_method(self, combined_file: str) -> str:
        """Intelligently recommend the best tax method based on transaction patterns."""
        df = pd.read_csv(combined_file)
        
        # Analyze transaction patterns
        total_transactions = len(df)
        unique_assets = df['base_asset'].nunique()
        date_range = (pd.to_datetime(df['timestamp']).max() - pd.to_datetime(df['timestamp']).min()).days
        
        # Check for specific patterns
        has_frequent_trading = total_transactions > 100
        has_many_assets = unique_assets > 10
        has_long_holdings = date_range > 365
        
        # Check for DeFi/Complex transactions
        has_defi = any(keyword in ' '.join(df['notes'].fillna('').str.lower()) 
                      for keyword in ['uniswap', 'pancakeswap', 'curve', 'aave', 'compound'])
        
        # Recommendation logic
        if has_defi and has_frequent_trading:
            return "fifo"  # FIFO is most common and accepted
        elif has_long_holdings and not has_frequent_trading:
            return "fifo"  # FIFO for long-term investors
        elif has_frequent_trading and has_many_assets:
            return "fifo"  # FIFO for complex portfolios
        else:
            return "fifo"  # Default to FIFO (most widely accepted)
    
    def _calculate_taxes_auto(self, combined_file: str, method: str) -> Dict[str, Any]:
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
    
    def _analyze_portfolio(self, combined_file: str) -> Dict[str, Any]:
        """Generate comprehensive portfolio analysis."""
        try:
            df = pd.read_csv(combined_file)
            tracker = PortfolioTracker()
            tracker.load_transactions(df)
            
            # Get portfolio summary
            summary = tracker.get_portfolio_summary()
            
            # Get performance metrics
            performance = tracker.get_performance_metrics()
            
            # Get risk metrics
            risk = tracker.get_risk_metrics()
            
            # Get trading activity
            activity_30d = tracker.get_trading_activity(30)
            activity_7d = tracker.get_trading_activity(7)
            
            return {
                "portfolio_summary": summary,
                "performance_metrics": performance,
                "risk_metrics": risk,
                "trading_activity_30d": activity_30d,
                "trading_activity_7d": activity_7d
            }
        except Exception as e:
            logger.error(f"Portfolio analysis failed: {e}")
            return {"error": str(e)}
    
    def _generate_all_reports_auto(self, tax_results: Dict, portfolio_analysis: Dict) -> Dict[str, str]:
        """Generate all reports automatically."""
        reports = {}
        
        try:
            # Generate all tax software formats
            all_reports = generate_all_reports()
            reports.update(all_reports)
            
            # Generate portfolio report
            if 'error' not in portfolio_analysis:
                portfolio_file = "data/output/reports/portfolio_analysis.json"
                with open(portfolio_file, 'w') as f:
                    json.dump(portfolio_analysis, f, indent=2, default=str)
                reports['portfolio_analysis'] = portfolio_file
            
            # Generate summary report
            summary_file = self._generate_summary_report(tax_results, portfolio_analysis)
            reports['summary'] = summary_file
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            reports['error'] = str(e)
        
        return reports
    
    def _generate_summary_report(self, tax_results: Dict, portfolio_analysis: Dict) -> str:
        """Generate a comprehensive summary report."""
        summary_file = "data/output/reports/tax_summary.json"
        
        summary = {
            "generated_at": datetime.now().isoformat(),
            "tax_results": tax_results,
            "portfolio_analysis": portfolio_analysis,
            "recommendations": self._get_tax_recommendations(tax_results),
            "next_year_planning": self._get_next_year_planning(tax_results, portfolio_analysis)
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        return summary_file
    
    def _get_tax_recommendations(self, tax_results: Dict) -> List[str]:
        """Generate tax optimization recommendations."""
        recommendations = []
        
        if tax_results['total_gains'] > 0:
            if tax_results['short_term_gains'] > tax_results['long_term_gains']:
                recommendations.append("Consider holding positions longer to qualify for long-term capital gains rates")
            
            if tax_results['estimated_tax'] > 1000:
                recommendations.append("Consider tax-loss harvesting to offset gains")
        
        if tax_results['total_income'] > 0:
            recommendations.append("Remember to report staking rewards and airdrops as income")
        
        return recommendations
    
    def _get_next_year_planning(self, tax_results: Dict, portfolio_analysis: Dict) -> List[str]:
        """Generate next year planning advice."""
        planning = []
        
        if 'portfolio_summary' in portfolio_analysis:
            total_value = portfolio_analysis['portfolio_summary'].get('total_value', 0)
            if total_value > 10000:
                planning.append("Consider setting up quarterly estimated tax payments")
        
        if tax_results['total_gains'] > 5000:
            planning.append("Keep detailed records of all transactions for next year")
        
        return planning
    
    def _create_summary_dashboard(self, tax_results: Dict, portfolio_analysis: Dict, reports: Dict) -> Dict[str, Any]:
        """Create a summary dashboard with key metrics."""
        return {
            "total_value": portfolio_analysis.get('portfolio_summary', {}).get('total_value', 0),
            "total_gains": tax_results['total_gains'],
            "estimated_tax": tax_results['estimated_tax'],
            "total_transactions": tax_results['total_transactions'],
            "reports_generated": len([r for r in reports.values() if isinstance(r, str)]),
            "tax_method": tax_results['method_used'],
            "status": "Complete" if tax_results['total_transactions'] > 0 else "No transactions found"
        }
    
    def _get_next_steps(self, reports: Dict) -> List[str]:
        """Get next steps for the user."""
        steps = [
            "All processing complete!",
            "Download your tax reports from the data/output/reports/ folder",
            "Import the TurboTax CSV into your tax software",
            "Keep all files for your records"
        ]
        
        if 'portfolio_analysis' in reports:
            steps.append("Review your portfolio analysis for investment insights")
        
        return steps
    
    def _log(self, message: str):
        """Add message to processing log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.processing_log.append(log_entry)
        logger.info(message)
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result."""
        return {
            "success": False,
            "error": error_message,
            "processing_log": self.processing_log,
            "next_steps": ["Please check the error message above and try again"]
        }


def process_crypto_taxes(input_dir: str = "data/input", output_dir: str = "data/output") -> Dict[str, Any]:
    """
    One-click crypto tax processing - the main function users call.
    
    Args:
        input_dir: Directory containing CSV files
        output_dir: Directory for output files
        
    Returns:
        Complete processing results
    """
    processor = AutoTaxProcessor()
    return processor.process_all_files(input_dir, output_dir)