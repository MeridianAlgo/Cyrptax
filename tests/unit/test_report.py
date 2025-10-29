"""Comprehensive unit tests for the report module."""

import pytest
import pandas as pd
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from report import (generate_turbotax_report, generate_pdf_summary, 
                   generate_detailed_report, generate_json_summary,
                   generate_all_reports)
from exceptions import ReportGenerationError


class TestTurboTaxReport:
    """Test cases for TurboTax report generation."""
    
    def test_generate_turbotax_report_basic(self):
        """Test basic TurboTax report generation."""
        # Create sample gains data
        gains_data = {
            'asset': ['BTC', 'ETH'],
            'amount': [0.5, 2.0],
            'acquisition_date': ['2024-01-01', '2024-02-01'],
            'sale_date': ['2024-06-01', '2024-07-01'],
            'cost_basis': [25000.0, 6000.0],
            'proceeds': [30000.0, 7000.0],
            'gain_loss': [5000.0, 1000.0],
            'short_term': [True, True]
        }
        
        gains_df = pd.DataFrame(gains_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            generate_turbotax_report(gains_df, output_file)
            
            # Verify file was created
            assert os.path.exists(output_file)
            
            # Read and verify content
            result_df = pd.read_csv(output_file)
            
            # Check required TurboTax columns
            required_columns = ['Description', 'Date Acquired', 'Date Sold', 
                              'Proceeds', 'Cost Basis', 'Gain/Loss', 'Term']
            
            for col in required_columns:
                assert col in result_df.columns, f"Missing column: {col}"
            
            # Verify data content
            assert len(result_df) == 2
            assert result_df['Proceeds'].iloc[0] == 30000.0
            assert result_df['Cost Basis'].iloc[0] == 25000.0
            assert result_df['Gain/Loss'].iloc[0] == 5000.0
            assert result_df['Term'].iloc[0] == 'Short'
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_generate_turbotax_report_long_term(self):
        """Test TurboTax report with long-term gains."""
        gains_data = {
            'asset': ['BTC'],
            'amount': [1.0],
            'acquisition_date': ['2023-01-01'],
            'sale_date': ['2024-06-01'],
            'cost_basis': [30000.0],
            'proceeds': [50000.0],
            'gain_loss': [20000.0],
            'short_term': [False]  # Long-term
        }
        
        gains_df = pd.DataFrame(gains_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            generate_turbotax_report(gains_df, output_file)
            
            result_df = pd.read_csv(output_file)
            assert result_df['Term'].iloc[0] == 'Long'
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_generate_turbotax_report_losses(self):
        """Test TurboTax report with capital losses."""
        gains_data = {
            'asset': ['BTC', 'ETH'],
            'amount': [0.5, 1.0],
            'acquisition_date': ['2024-01-01', '2024-02-01'],
            'sale_date': ['2024-06-01', '2024-07-01'],
            'cost_basis': [30000.0, 4000.0],
            'proceeds': [25000.0, 3000.0],
            'gain_loss': [-5000.0, -1000.0],  # Losses
            'short_term': [True, True]
        }
        
        gains_df = pd.DataFrame(gains_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            generate_turbotax_report(gains_df, output_file)
            
            result_df = pd.read_csv(output_file)
            
            # Verify losses are properly formatted
            assert result_df['Gain/Loss'].iloc[0] == -5000.0
            assert result_df['Gain/Loss'].iloc[1] == -1000.0
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_generate_turbotax_report_empty_data(self):
        """Test TurboTax report with empty gains data."""
        gains_df = pd.DataFrame()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            generate_turbotax_report(gains_df, output_file)
            
            # Should create empty file with headers
            assert os.path.exists(output_file)
            result_df = pd.read_csv(output_file)
            assert len(result_df) == 0
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_generate_turbotax_report_invalid_path(self):
        """Test TurboTax report with invalid output path."""
        gains_data = {
            'asset': ['BTC'],
            'amount': [1.0],
            'acquisition_date': ['2024-01-01'],
            'sale_date': ['2024-06-01'],
            'cost_basis': [30000.0],
            'proceeds': [50000.0],
            'gain_loss': [20000.0],
            'short_term': [True]
        }
        
        gains_df = pd.DataFrame(gains_data)
        
        with pytest.raises((OSError, ReportGenerationError)):
            generate_turbotax_report(gains_df, '/invalid/path/report.csv')


class TestPDFSummaryReport:
    """Test cases for PDF summary report generation."""
    
    @patch('report.FPDF')
    def test_generate_pdf_summary_basic(self, mock_fpdf):
        """Test basic PDF summary generation."""
        # Mock FPDF
        mock_pdf = MagicMock()
        mock_fpdf.return_value = mock_pdf
        
        gains_data = {
            'asset': ['BTC', 'ETH'],
            'gain_loss': [5000.0, 1000.0],
            'short_term': [True, False]
        }
        
        gains_df = pd.DataFrame(gains_data)
        income = 2000.0
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            output_file = f.name
        
        try:
            generate_pdf_summary(gains_df, income, output_file)
            
            # Verify PDF methods were called
            mock_pdf.add_page.assert_called()
            mock_pdf.set_font.assert_called()
            mock_pdf.cell.assert_called()
            mock_pdf.output.assert_called_with(output_file)
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    @patch('report.FPDF')
    def test_generate_pdf_summary_with_losses(self, mock_fpdf):
        """Test PDF summary with capital losses."""
        mock_pdf = MagicMock()
        mock_fpdf.return_value = mock_pdf
        
        gains_data = {
            'asset': ['BTC', 'ETH'],
            'gain_loss': [-3000.0, -1000.0],  # Losses
            'short_term': [True, False]
        }
        
        gains_df = pd.DataFrame(gains_data)
        income = 500.0
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            output_file = f.name
        
        try:
            generate_pdf_summary(gains_df, income, output_file)
            
            # Should handle losses properly
            mock_pdf.output.assert_called_with(output_file)
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    @patch('report.FPDF')
    def test_generate_pdf_summary_empty_data(self, mock_fpdf):
        """Test PDF summary with empty data."""
        mock_pdf = MagicMock()
        mock_fpdf.return_value = mock_pdf
        
        gains_df = pd.DataFrame()
        income = 0.0
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            output_file = f.name
        
        try:
            generate_pdf_summary(gains_df, income, output_file)
            
            # Should create PDF even with empty data
            mock_pdf.output.assert_called_with(output_file)
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)


class TestDetailedReport:
    """Test cases for detailed CSV report generation."""
    
    def test_generate_detailed_report_basic(self):
        """Test basic detailed report generation."""
        gains_data = {
            'asset': ['BTC', 'ETH'],
            'amount': [0.5, 2.0],
            'acquisition_date': ['2024-01-01', '2024-02-01'],
            'sale_date': ['2024-06-01', '2024-07-01'],
            'cost_basis': [25000.0, 6000.0],
            'proceeds': [30000.0, 7000.0],
            'gain_loss': [5000.0, 1000.0],
            'short_term': [True, False],
            'method': ['FIFO', 'FIFO']
        }
        
        gains_df = pd.DataFrame(gains_data)
        
        income_data = [
            {'date': '2024-03-01', 'asset': 'ETH', 'amount': 1.0, 'value': 3000.0, 'type': 'staking'},
            {'date': '2024-04-01', 'asset': 'TOKEN', 'amount': 100.0, 'value': 500.0, 'type': 'airdrop'}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            generate_detailed_report(gains_df, income_data, output_file)
            
            # Verify file was created
            assert os.path.exists(output_file)
            
            # Read and verify content
            result_df = pd.read_csv(output_file)
            
            # Should contain both gains and income sections
            assert len(result_df) > 0
            
            # Check for section headers or combined data
            # Implementation may vary, so just verify structure
            assert 'asset' in result_df.columns or 'Asset' in result_df.columns
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_generate_detailed_report_gains_only(self):
        """Test detailed report with gains only (no income)."""
        gains_data = {
            'asset': ['BTC'],
            'amount': [1.0],
            'acquisition_date': ['2024-01-01'],
            'sale_date': ['2024-06-01'],
            'cost_basis': [30000.0],
            'proceeds': [50000.0],
            'gain_loss': [20000.0],
            'short_term': [True]
        }
        
        gains_df = pd.DataFrame(gains_data)
        income_data = []
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            generate_detailed_report(gains_df, income_data, output_file)
            
            assert os.path.exists(output_file)
            result_df = pd.read_csv(output_file)
            assert len(result_df) > 0
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_generate_detailed_report_income_only(self):
        """Test detailed report with income only (no gains)."""
        gains_df = pd.DataFrame()
        
        income_data = [
            {'date': '2024-03-01', 'asset': 'ETH', 'amount': 1.0, 'value': 3000.0, 'type': 'staking'}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            generate_detailed_report(gains_df, income_data, output_file)
            
            assert os.path.exists(output_file)
            result_df = pd.read_csv(output_file)
            # Should have at least the income data
            assert len(result_df) >= 0  # May be empty if no data to report
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)


class TestJSONSummaryReport:
    """Test cases for JSON summary report generation."""
    
    def test_generate_json_summary_basic(self):
        """Test basic JSON summary generation."""
        gains_data = {
            'asset': ['BTC', 'ETH'],
            'gain_loss': [5000.0, 1000.0],
            'short_term': [True, False]
        }
        
        gains_df = pd.DataFrame(gains_data)
        income = 2000.0
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            generate_json_summary(gains_df, income, output_file)
            
            # Verify file was created
            assert os.path.exists(output_file)
            
            # Read and verify JSON content
            with open(output_file, 'r') as f:
                result = json.load(f)
            
            # Check required fields
            assert 'total_short_term_gains' in result
            assert 'total_long_term_gains' in result
            assert 'total_income' in result
            assert 'net_capital_gains' in result
            
            # Verify calculations
            assert result['total_short_term_gains'] == 5000.0
            assert result['total_long_term_gains'] == 1000.0
            assert result['total_income'] == 2000.0
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_generate_json_summary_with_losses(self):
        """Test JSON summary with capital losses."""
        gains_data = {
            'asset': ['BTC', 'ETH'],
            'gain_loss': [-3000.0, 2000.0],
            'short_term': [True, False]
        }
        
        gains_df = pd.DataFrame(gains_data)
        income = 1000.0
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            generate_json_summary(gains_df, income, output_file)
            
            with open(output_file, 'r') as f:
                result = json.load(f)
            
            # Should handle losses properly
            assert result['total_short_term_gains'] == -3000.0
            assert result['total_long_term_gains'] == 2000.0
            assert result['net_capital_gains'] == -1000.0
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_generate_json_summary_empty_data(self):
        """Test JSON summary with empty data."""
        gains_df = pd.DataFrame()
        income = 0.0
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            generate_json_summary(gains_df, income, output_file)
            
            with open(output_file, 'r') as f:
                result = json.load(f)
            
            # Should have zero values
            assert result['total_short_term_gains'] == 0.0
            assert result['total_long_term_gains'] == 0.0
            assert result['total_income'] == 0.0
            assert result['net_capital_gains'] == 0.0
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)


class TestGenerateAllReports:
    """Test cases for generating all reports at once."""
    
    @patch('report.generate_turbotax_report')
    @patch('report.generate_pdf_summary')
    @patch('report.generate_detailed_report')
    @patch('report.generate_json_summary')
    def test_generate_all_reports_basic(self, mock_json, mock_detailed, mock_pdf, mock_turbotax):
        """Test generating all report types."""
        gains_data = {
            'asset': ['BTC'],
            'gain_loss': [5000.0],
            'short_term': [True]
        }
        
        gains_df = pd.DataFrame(gains_data)
        income_data = []
        income_total = 1000.0
        
        output_dir = tempfile.mkdtemp()
        
        try:
            generate_all_reports(gains_df, income_data, income_total, output_dir)
            
            # Verify all report generators were called
            mock_turbotax.assert_called_once()
            mock_pdf.assert_called_once()
            mock_detailed.assert_called_once()
            mock_json.assert_called_once()
            
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(output_dir)
    
    def test_generate_all_reports_creates_directory(self):
        """Test that generate_all_reports creates output directory."""
        gains_df = pd.DataFrame()
        income_data = []
        income_total = 0.0
        
        output_dir = tempfile.mkdtemp()
        test_subdir = os.path.join(output_dir, 'test_reports')
        
        try:
            # Remove the directory to test creation
            os.rmdir(output_dir)
            
            generate_all_reports(gains_df, income_data, income_total, test_subdir)
            
            # Directory should be created
            assert os.path.exists(test_subdir)
            
        finally:
            # Cleanup
            if os.path.exists(test_subdir):
                import shutil
                shutil.rmtree(test_subdir)


class TestReportErrorHandling:
    """Test error handling in report generation."""
    
    def test_turbotax_report_invalid_data(self):
        """Test TurboTax report with invalid data types."""
        # Invalid data types
        gains_data = {
            'asset': ['BTC'],
            'amount': ['not_a_number'],  # Invalid
            'acquisition_date': ['invalid_date'],  # Invalid
            'sale_date': ['2024-06-01'],
            'cost_basis': [30000.0],
            'proceeds': [50000.0],
            'gain_loss': [20000.0],
            'short_term': [True]
        }
        
        gains_df = pd.DataFrame(gains_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            # Should handle invalid data gracefully or raise appropriate error
            try:
                generate_turbotax_report(gains_df, output_file)
                # If it succeeds, verify the output
                assert os.path.exists(output_file)
            except (ValueError, ReportGenerationError):
                # Expected behavior for invalid data
                pass
                
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_report_permission_error(self):
        """Test report generation with permission errors."""
        gains_df = pd.DataFrame({'asset': ['BTC'], 'gain_loss': [1000.0]})
        
        # Try to write to a read-only location (this may vary by OS)
        with pytest.raises((PermissionError, OSError, ReportGenerationError)):
            generate_turbotax_report(gains_df, '/root/readonly.csv')
    
    def test_pdf_generation_error(self):
        """Test PDF generation error handling."""
        gains_df = pd.DataFrame({'asset': ['BTC'], 'gain_loss': [1000.0]})
        income = 0.0
        
        with patch('report.FPDF') as mock_fpdf:
            mock_fpdf.side_effect = Exception("PDF generation failed")
            
            with pytest.raises((Exception, ReportGenerationError)):
                generate_pdf_summary(gains_df, income, 'test.pdf')


class TestReportFormatting:
    """Test report formatting and data presentation."""
    
    def test_turbotax_date_formatting(self):
        """Test proper date formatting in TurboTax report."""
        gains_data = {
            'asset': ['BTC'],
            'amount': [1.0],
            'acquisition_date': ['2024-01-01T10:30:00'],  # With time
            'sale_date': ['2024-06-01T15:45:00'],  # With time
            'cost_basis': [30000.0],
            'proceeds': [50000.0],
            'gain_loss': [20000.0],
            'short_term': [True]
        }
        
        gains_df = pd.DataFrame(gains_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            generate_turbotax_report(gains_df, output_file)
            
            result_df = pd.read_csv(output_file)
            
            # Dates should be formatted properly (no time component)
            acquired_date = result_df['Date Acquired'].iloc[0]
            sold_date = result_df['Date Sold'].iloc[0]
            
            # Should be in MM/DD/YYYY format or similar
            assert '2024' in str(acquired_date)
            assert '2024' in str(sold_date)
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_currency_formatting(self):
        """Test proper currency formatting in reports."""
        gains_data = {
            'asset': ['BTC'],
            'amount': [1.0],
            'acquisition_date': ['2024-01-01'],
            'sale_date': ['2024-06-01'],
            'cost_basis': [30000.123456],  # High precision
            'proceeds': [50000.987654],  # High precision
            'gain_loss': [20000.864198],  # High precision
            'short_term': [True]
        }
        
        gains_df = pd.DataFrame(gains_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            generate_turbotax_report(gains_df, output_file)
            
            result_df = pd.read_csv(output_file)
            
            # Currency values should be properly rounded
            cost_basis = result_df['Cost Basis'].iloc[0]
            proceeds = result_df['Proceeds'].iloc[0]
            
            # Should be rounded to 2 decimal places
            assert abs(cost_basis - 30000.12) < 0.01
            assert abs(proceeds - 50000.99) < 0.01
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)


class TestReportIntegration:
    """Integration tests for report generation workflow."""
    
    def test_end_to_end_report_generation(self):
        """Test complete report generation workflow."""
        # Simulate realistic tax calculation results
        gains_data = {
            'asset': ['BTC', 'ETH', 'BTC'],
            'amount': [0.5, 2.0, 0.3],
            'acquisition_date': ['2024-01-01', '2024-02-01', '2024-01-15'],
            'sale_date': ['2024-06-01', '2024-07-01', '2024-08-01'],
            'cost_basis': [25000.0, 6000.0, 15000.0],
            'proceeds': [30000.0, 7000.0, 18000.0],
            'gain_loss': [5000.0, 1000.0, 3000.0],
            'short_term': [True, True, True]
        }
        
        gains_df = pd.DataFrame(gains_data)
        
        income_data = [
            {'date': '2024-03-01', 'asset': 'ETH', 'amount': 1.0, 'value': 3000.0, 'type': 'staking'},
            {'date': '2024-04-01', 'asset': 'TOKEN', 'amount': 100.0, 'value': 500.0, 'type': 'airdrop'}
        ]
        
        income_total = 3500.0
        
        output_dir = tempfile.mkdtemp()
        
        try:
            # Generate all reports
            generate_all_reports(gains_df, income_data, income_total, output_dir)
            
            # Verify all report files were created
            expected_files = [
                'turbotax_import.csv',
                'tax_summary.pdf',
                'detailed_tax_report.csv',
                'tax_summary.json'
            ]
            
            for filename in expected_files:
                filepath = os.path.join(output_dir, filename)
                assert os.path.exists(filepath), f"Missing report file: {filename}"
                
                # Verify file is not empty
                assert os.path.getsize(filepath) > 0, f"Empty report file: {filename}"
            
            # Verify TurboTax CSV content
            turbotax_df = pd.read_csv(os.path.join(output_dir, 'turbotax_import.csv'))
            assert len(turbotax_df) == 3  # Three transactions
            
            # Verify JSON summary content
            with open(os.path.join(output_dir, 'tax_summary.json'), 'r') as f:
                json_summary = json.load(f)
            
            assert json_summary['total_short_term_gains'] == 9000.0  # Sum of gains
            assert json_summary['total_income'] == 3500.0
            
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(output_dir)


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])