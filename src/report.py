"""Report generation module for creating tax reports in various formats."""

import pandas as pd
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
import logging

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    logging.warning("fpdf2 not available. PDF reports will be disabled.")

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Handles generation of various tax report formats."""
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or config.get('output', 'reports_dir', 'output/reports')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_turbotax_report(self, gains_file: str = None, output_file: str = None) -> str:
        """
        Generate TurboTax-compatible CSV report from gains/losses data.
        
        Args:
            gains_file: Path to gains/losses CSV file
            output_file: Output path for TurboTax CSV
            
        Returns:
            Path to generated TurboTax report
        """
        if gains_file is None:
            gains_file = os.path.join(self.output_dir, 'gains_losses.csv')
        
        if output_file is None:
            output_file = os.path.join(self.output_dir, 'turbotax_import.csv')
        
        try:
            df = pd.read_csv(gains_file)
        except FileNotFoundError:
            logger.error(f"Gains file not found: {gains_file}")
            raise
        
        if df.empty:
            logger.warning("No gains/losses data to export")
            return output_file
        
        # Convert to TurboTax format
        turbotax_df = pd.DataFrame({
            'Description': df['asset'] + ' - ' + df['method'].str.upper() + ' Sale',
            'Date Acquired': pd.to_datetime(df['acquisition_date']).dt.strftime('%m/%d/%Y'),
            'Date Sold': pd.to_datetime(df['date']).dt.strftime('%m/%d/%Y'),
            'Proceeds': df['proceeds'].round(2),
            'Cost Basis': df['cost_basis'].round(2),
            'Gain/Loss': df['gain_loss'].round(2),
            'Term': df['short_term'].map({True: 'Short', False: 'Long'}),
            'Asset': df['asset'],
            'Amount': df['amount']
        })
        
        # Sort by date sold
        turbotax_df = turbotax_df.sort_values('Date Sold')
        
        # Save to CSV
        turbotax_df.to_csv(output_file, index=False)
        
        logger.info(f"TurboTax report saved to {output_file}")
        logger.info(f"Generated {len(turbotax_df)} capital gains/loss entries")
        
        return output_file
    
    def generate_pdf_summary(self, gains_df: Optional[pd.DataFrame] = None, 
                           income: float = 0, output_file: str = None) -> str:
        """
        Generate PDF summary report with key tax figures.
        
        Args:
            gains_df: DataFrame with gains/losses data
            income: Total income amount
            output_file: Output path for PDF
            
        Returns:
            Path to generated PDF report
        """
        if not FPDF_AVAILABLE:
            logger.error("PDF generation not available. Install fpdf2: pip install fpdf2")
            raise ImportError("fpdf2 package required for PDF generation")
        
        if output_file is None:
            output_file = os.path.join(self.output_dir, 'tax_summary.pdf')
        
        # Load gains data if not provided
        if gains_df is None:
            gains_file = os.path.join(self.output_dir, 'gains_losses.csv')
            try:
                gains_df = pd.read_csv(gains_file)
            except FileNotFoundError:
                logger.warning("No gains file found, creating summary with zero gains")
                gains_df = pd.DataFrame()
        
        # Calculate summary statistics
        if not gains_df.empty:
            short_term_gains = gains_df[gains_df['short_term']]['gain_loss'].sum()
            long_term_gains = gains_df[~gains_df['short_term']]['gain_loss'].sum()
            total_gains = gains_df['gain_loss'].sum()
            total_proceeds = gains_df['proceeds'].sum()
            total_cost_basis = gains_df['cost_basis'].sum()
            num_transactions = len(gains_df)
        else:
            short_term_gains = long_term_gains = total_gains = 0
            total_proceeds = total_cost_basis = 0
            num_transactions = 0
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        
        # Title
        pdf.cell(200, 10, txt="Cryptocurrency Tax Summary", ln=1, align='C')
        pdf.ln(10)
        
        # Generation info
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 5, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1)
        pdf.ln(5)
        
        # Summary section
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 8, txt="Capital Gains/Losses Summary", ln=1)
        pdf.set_font("Arial", size=11)
        
        pdf.cell(100, 6, txt=f"Short-term gains/losses:", ln=0)
        pdf.cell(100, 6, txt=f"${short_term_gains:,.2f}", ln=1, align='R')
        
        pdf.cell(100, 6, txt=f"Long-term gains/losses:", ln=0)
        pdf.cell(100, 6, txt=f"${long_term_gains:,.2f}", ln=1, align='R')
        
        pdf.cell(100, 6, txt=f"Total gains/losses:", ln=0)
        pdf.set_font("Arial", size=11, style='B')
        pdf.cell(100, 6, txt=f"${total_gains:,.2f}", ln=1, align='R')
        pdf.set_font("Arial", size=11)
        
        pdf.ln(5)
        
        # Income section
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 8, txt="Income Summary", ln=1)
        pdf.set_font("Arial", size=11)
        
        pdf.cell(100, 6, txt=f"Staking/Airdrop income:", ln=0)
        pdf.set_font("Arial", size=11, style='B')
        pdf.cell(100, 6, txt=f"${income:,.2f}", ln=1, align='R')
        pdf.set_font("Arial", size=11)
        
        pdf.ln(5)
        
        # Transaction details
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 8, txt="Transaction Details", ln=1)
        pdf.set_font("Arial", size=11)
        
        pdf.cell(100, 6, txt=f"Total transactions processed:", ln=0)
        pdf.cell(100, 6, txt=f"{num_transactions:,}", ln=1, align='R')
        
        pdf.cell(100, 6, txt=f"Total proceeds:", ln=0)
        pdf.cell(100, 6, txt=f"${total_proceeds:,.2f}", ln=1, align='R')
        
        pdf.cell(100, 6, txt=f"Total cost basis:", ln=0)
        pdf.cell(100, 6, txt=f"${total_cost_basis:,.2f}", ln=1, align='R')
        
        pdf.ln(10)
        
        # Disclaimer
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 5, txt="DISCLAIMER:", ln=1, style='B')
        pdf.multi_cell(0, 5, txt="This report is for informational purposes only and does not constitute tax advice. "
                                 "Consult with a qualified tax professional for your specific situation. "
                                 "The authors are not responsible for any errors or omissions in tax calculations.")
        
        # Save PDF
        pdf.output(output_file)
        
        logger.info(f"PDF summary saved to {output_file}")
        
        return output_file
    
    def generate_detailed_report(self, gains_file: str = None, income_file: str = None, 
                               output_file: str = None) -> str:
        """
        Generate detailed CSV report with all transaction information.
        
        Args:
            gains_file: Path to gains/losses CSV
            income_file: Path to income events CSV
            output_file: Output path for detailed report
            
        Returns:
            Path to generated detailed report
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, 'detailed_tax_report.csv')
        
        # Load data files
        gains_df = pd.DataFrame()
        income_df = pd.DataFrame()
        
        if gains_file is None:
            gains_file = os.path.join(self.output_dir, 'gains_losses.csv')
        
        if income_file is None:
            income_file = os.path.join(self.output_dir, 'income_events.csv')
        
        try:
            if os.path.exists(gains_file):
                gains_df = pd.read_csv(gains_file)
        except Exception as e:
            logger.warning(f"Could not load gains file: {e}")
        
        try:
            if os.path.exists(income_file):
                income_df = pd.read_csv(income_file)
        except Exception as e:
            logger.warning(f"Could not load income file: {e}")
        
        # Combine and format data
        all_events = []
        
        # Add gains/losses events
        for _, row in gains_df.iterrows():
            event = {
                'Date': pd.to_datetime(row['date']).strftime('%Y-%m-%d'),
                'Type': 'Capital Gain/Loss',
                'Asset': row['asset'],
                'Amount': row['amount'],
                'Proceeds': row.get('proceeds', 0),
                'Cost Basis': row.get('cost_basis', 0),
                'Gain/Loss': row.get('gain_loss', 0),
                'Term': 'Short-term' if row.get('short_term', True) else 'Long-term',
                'Method': row.get('method', '').upper(),
                'Acquisition Date': pd.to_datetime(row.get('acquisition_date', '')).strftime('%Y-%m-%d') if pd.notna(row.get('acquisition_date')) else '',
                'Holding Period (Days)': row.get('holding_period_days', ''),
                'Notes': row.get('note', '')
            }
            all_events.append(event)
        
        # Add income events
        for _, row in income_df.iterrows():
            event = {
                'Date': pd.to_datetime(row['date']).strftime('%Y-%m-%d'),
                'Type': f"Income - {row.get('type', 'Unknown')}",
                'Asset': row['asset'],
                'Amount': row['amount'],
                'Proceeds': row.get('income_amount', 0),
                'Cost Basis': row.get('income_amount', 0),  # Income becomes cost basis
                'Gain/Loss': 0,  # No gain/loss on income receipt
                'Term': 'N/A',
                'Method': 'N/A',
                'Acquisition Date': pd.to_datetime(row['date']).strftime('%Y-%m-%d'),
                'Holding Period (Days)': 0,
                'Notes': f"Fair market value: ${row.get('price', 0):.2f}"
            }
            all_events.append(event)
        
        # Create DataFrame and sort by date
        if all_events:
            detailed_df = pd.DataFrame(all_events)
            detailed_df = detailed_df.sort_values('Date')
        else:
            detailed_df = pd.DataFrame(columns=[
                'Date', 'Type', 'Asset', 'Amount', 'Proceeds', 'Cost Basis', 
                'Gain/Loss', 'Term', 'Method', 'Acquisition Date', 
                'Holding Period (Days)', 'Notes'
            ])
        
        # Save to CSV
        detailed_df.to_csv(output_file, index=False)
        
        logger.info(f"Detailed report saved to {output_file}")
        logger.info(f"Generated report with {len(detailed_df)} total events")
        
        return output_file
    
    def generate_summary_json(self, gains_df: Optional[pd.DataFrame] = None, 
                            income: float = 0, method: str = 'fifo') -> str:
        """
        Generate JSON summary with key statistics.
        
        Args:
            gains_df: DataFrame with gains/losses data
            income: Total income amount
            method: Tax calculation method used
            
        Returns:
            Path to generated JSON summary
        """
        output_file = os.path.join(self.output_dir, 'summary.json')
        
        # Calculate statistics
        if gains_df is not None and not gains_df.empty:
            short_term_gains = gains_df[gains_df['short_term']]['gain_loss'].sum()
            long_term_gains = gains_df[~gains_df['short_term']]['gain_loss'].sum()
            total_gains = gains_df['gain_loss'].sum()
            num_transactions = len(gains_df)
            assets_traded = gains_df['asset'].nunique()
        else:
            short_term_gains = long_term_gains = total_gains = 0
            num_transactions = assets_traded = 0
        
        summary = {
            'generated_at': datetime.now().isoformat(),
            'method': method.upper(),
            'capital_gains': {
                'short_term': round(short_term_gains, 2),
                'long_term': round(long_term_gains, 2),
                'total': round(total_gains, 2)
            },
            'income': {
                'total': round(income, 2)
            },
            'statistics': {
                'total_transactions': num_transactions,
                'assets_traded': assets_traded
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"JSON summary saved to {output_file}")
        
        return output_file


def generate_turbotax_report(gains_file: str = None, output_file: str = None) -> str:
    """Convenience function to generate TurboTax report."""
    generator = ReportGenerator()
    return generator.generate_turbotax_report(gains_file, output_file)


def generate_pdf_summary(gains_df: pd.DataFrame = None, income: float = 0, 
                        output_file: str = None) -> str:
    """Convenience function to generate PDF summary."""
    generator = ReportGenerator()
    return generator.generate_pdf_summary(gains_df, income, output_file)


def generate_all_reports(gains_df: pd.DataFrame = None, income: float = 0, 
                        method: str = 'fifo') -> Dict[str, str]:
    """
    Generate all available report formats.
    
    Args:
        gains_df: DataFrame with gains/losses data
        income: Total income amount
        method: Tax calculation method used
        
    Returns:
        Dictionary mapping report type to file path
    """
    generator = ReportGenerator()
    reports = {}
    
    try:
        reports['turbotax'] = generator.generate_turbotax_report()
    except Exception as e:
        logger.error(f"Failed to generate TurboTax report: {e}")
    
    try:
        reports['pdf_summary'] = generator.generate_pdf_summary(gains_df, income)
    except Exception as e:
        logger.error(f"Failed to generate PDF summary: {e}")
    
    try:
        reports['detailed'] = generator.generate_detailed_report()
    except Exception as e:
        logger.error(f"Failed to generate detailed report: {e}")
    
    try:
        reports['json_summary'] = generator.generate_summary_json(gains_df, income, method)
    except Exception as e:
        logger.error(f"Failed to generate JSON summary: {e}")
    
    return reports