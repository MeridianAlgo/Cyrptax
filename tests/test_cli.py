"""Comprehensive integration tests for the CLI interface."""

import pytest
import subprocess
import tempfile
import os
import sys
from pathlib import Path
import json
import pandas as pd
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import CLI functions for direct testing
from main import (cmd_normalize, cmd_calculate, cmd_report, cmd_validate, 
                 cmd_auto_process, cmd_detect, cmd_list_exchanges)


class TestCLICommands:
    """Test CLI command functions directly."""
    
    def test_cmd_normalize_basic(self):
        """Test basic normalize command."""
        # Create test input file
        test_data = """time,type,base-asset,quantity,quote-asset,total,fee,fee-currency
2024-01-01T00:00:00,buy,BTC,1.0,USDT,50000.0,25.0,USDT
2024-06-01T00:00:00,sell,BTC,0.5,USDT,30000.0,15.0,USDT"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            # Mock command line arguments
            args = MagicMock()
            args.input_file = input_file
            args.exchange = 'binance'
            args.output = output_file
            args.fetch_prices = False
            args.remove_duplicates = False
            args.sheet = None
            
            # Test normalize command
            cmd_normalize(args)
            
            # Verify output file was created
            assert os.path.exists(output_file)
            
            # Verify content
            df = pd.read_csv(output_file)
            assert len(df) == 2
            assert 'base_asset' in df.columns
            
        finally:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_cmd_calculate_basic(self):
        """Test basic calculate command."""
        # Create normalized test data
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,1.0,USD,50000.0,25.0,USD,
2024-06-01T00:00:00,sell,BTC,0.5,USD,30000.0,15.0,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            args = MagicMock()
            args.input_file = input_file
            args.method = 'fifo'
            args.currency = 'usd'
            args.output = output_file
            
            cmd_calculate(args)
            
            # Verify output file was created
            assert os.path.exists(output_file)
            
        finally:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    @patch('main.generate_all_reports')
    def test_cmd_report_all(self, mock_generate_all):
        """Test report command with --all flag."""
        args = MagicMock()
        args.turbotax = False
        args.pdf = False
        args.detailed = False
        args.json = False
        args.all = True
        args.output_dir = 'output/reports'
        
        cmd_report(args)
        
        # Should call generate_all_reports
        mock_generate_all.assert_called_once()
    
    def test_cmd_validate_basic(self):
        """Test validate command."""
        # Create test data with some issues
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,1.0,USD,50000.0,25.0,USD,
2024-01-01T00:00:00,buy,BTC,1.0,USD,50000.0,25.0,USD,
2024-06-01T00:00:00,sell,BTC,2.5,USD,30000.0,15.0,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            args = MagicMock()
            args.input_file = input_file
            
            # Should not raise exception
            cmd_validate(args)
            
        finally:
            os.unlink(input_file)
    
    @patch('main.auto_process_input_folder')
    def test_cmd_auto_process(self, mock_auto_process):
        """Test auto-process command."""
        mock_auto_process.return_value = [
            {'status': 'success', 'input_file': 'test.csv', 'output_file': 'test_normalized.csv'}
        ]
        
        args = MagicMock()
        args.input_dir = 'input'
        args.output_dir = 'output'
        args.no_interactive = False
        
        cmd_auto_process(args)
        
        mock_auto_process.assert_called_once_with('input', 'output', True)
    
    @patch('main.ExchangeDetector')
    def test_cmd_detect_folder(self, mock_detector_class):
        """Test detect command for folder scanning."""
        mock_detector = MagicMock()
        mock_detector.scan_input_folder.return_value = [
            {
                'file_name': 'test.csv',
                'detected_exchange': 'binance',
                'confidence': 0.95,
                'needs_confirmation': False
            }
        ]
        mock_detector_class.return_value = mock_detector
        
        args = MagicMock()
        args.file = None
        args.input_dir = 'input'
        args.normalize = False
        args.output = None
        
        cmd_detect(args)
        
        mock_detector.scan_input_folder.assert_called_once_with('input')
    
    def test_cmd_list_exchanges(self):
        """Test list-exchanges command."""
        args = MagicMock()
        
        # Should not raise exception
        cmd_list_exchanges(args)


class TestCLISubprocess:
    """Test CLI through subprocess calls."""
    
    def test_cli_help(self):
        """Test CLI help output."""
        result = subprocess.run([
            sys.executable, 'src/main.py', '--help'
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        
        assert result.returncode == 0
        assert 'usage:' in result.stdout.lower()
        assert 'normalize' in result.stdout
        assert 'calculate' in result.stdout
        assert 'report' in result.stdout
    
    def test_cli_list_exchanges(self):
        """Test list-exchanges command via subprocess."""
        result = subprocess.run([
            sys.executable, 'src/main.py', 'list-exchanges'
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        
        assert result.returncode == 0
        assert 'binance' in result.stdout.lower()
        assert 'coinbase' in result.stdout.lower()
        assert 'kraken' in result.stdout.lower()
    
    def test_cli_normalize_subprocess(self):
        """Test normalize command via subprocess."""
        # Create test input file
        test_data = """time,type,base-asset,quantity,quote-asset,total,fee,fee-currency
2024-01-01T00:00:00,buy,BTC,1.0,USDT,50000.0,25.0,USDT"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            result = subprocess.run([
                sys.executable, 'src/main.py', 'normalize',
                input_file, 'binance', '--output', output_file
            ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
            
            # Should succeed
            assert result.returncode == 0
            assert os.path.exists(output_file)
            
        finally:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_cli_invalid_command(self):
        """Test CLI with invalid command."""
        result = subprocess.run([
            sys.executable, 'src/main.py', 'invalid-command'
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        
        assert result.returncode != 0
        assert 'invalid choice' in result.stderr.lower() or 'error' in result.stderr.lower()
    
    def test_cli_normalize_missing_file(self):
        """Test normalize command with missing input file."""
        result = subprocess.run([
            sys.executable, 'src/main.py', 'normalize',
            'nonexistent.csv', 'binance'
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        
        assert result.returncode != 0
        # Should indicate file not found
        assert 'not found' in result.stderr.lower() or 'error' in result.stderr.lower()
    
    def test_cli_normalize_invalid_exchange(self):
        """Test normalize command with invalid exchange."""
        # Create dummy file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\nval1,val2")
            input_file = f.name
        
        try:
            result = subprocess.run([
                sys.executable, 'src/main.py', 'normalize',
                input_file, 'invalid_exchange'
            ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
            
            assert result.returncode != 0
            # Should indicate unsupported exchange
            assert 'unsupported' in result.stderr.lower() or 'error' in result.stderr.lower()
            
        finally:
            os.unlink(input_file)


class TestCLIWorkflows:
    """Test complete CLI workflows."""
    
    def test_normalize_calculate_report_workflow(self):
        """Test complete workflow: normalize -> calculate -> report."""
        # Create test input
        test_data = """time,type,base-asset,quantity,quote-asset,total,fee,fee-currency
2024-01-01T00:00:00,buy,BTC,1.0,USDT,50000.0,25.0,USDT
2024-06-01T00:00:00,sell,BTC,0.5,USDT,30000.0,15.0,USDT"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        # Create temporary files for each step
        normalized_file = tempfile.mktemp(suffix='.csv')
        calculated_file = tempfile.mktemp(suffix='.csv')
        report_dir = tempfile.mkdtemp()
        
        try:
            # Step 1: Normalize
            args1 = MagicMock()
            args1.input_file = input_file
            args1.exchange = 'binance'
            args1.output = normalized_file
            args1.fetch_prices = False
            args1.remove_duplicates = False
            args1.sheet = None
            
            cmd_normalize(args1)
            assert os.path.exists(normalized_file)
            
            # Step 2: Calculate
            args2 = MagicMock()
            args2.input_file = normalized_file
            args2.method = 'fifo'
            args2.currency = 'usd'
            args2.output = calculated_file
            
            cmd_calculate(args2)
            assert os.path.exists(calculated_file)
            
            # Step 3: Report (mock to avoid file dependencies)
            with patch('main.generate_all_reports') as mock_reports:
                args3 = MagicMock()
                args3.turbotax = False
                args3.pdf = False
                args3.detailed = False
                args3.json = False
                args3.all = True
                args3.output_dir = report_dir
                
                cmd_report(args3)
                mock_reports.assert_called_once()
            
        finally:
            # Cleanup
            for file_path in [input_file, normalized_file, calculated_file]:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            
            import shutil
            if os.path.exists(report_dir):
                shutil.rmtree(report_dir)
    
    @patch('main.auto_process_input_folder')
    def test_auto_process_workflow(self, mock_auto_process):
        """Test auto-process workflow."""
        # Mock successful auto-processing
        mock_auto_process.return_value = [
            {
                'input_file': 'input/binance.csv',
                'output_file': 'output/binance_normalized.csv',
                'exchange_used': 'binance',
                'detection_confidence': 0.95,
                'status': 'success'
            },
            {
                'input_file': 'input/coinbase.csv',
                'output_file': 'output/coinbase_normalized.csv',
                'exchange_used': 'coinbase',
                'detection_confidence': 0.88,
                'status': 'success'
            }
        ]
        
        args = MagicMock()
        args.input_dir = 'input'
        args.output_dir = 'output'
        args.no_interactive = True
        
        cmd_auto_process(args)
        
        # Should process both files
        mock_auto_process.assert_called_once_with('input', 'output', False)


class TestCLIErrorHandling:
    """Test CLI error handling scenarios."""
    
    def test_normalize_with_corrupted_file(self):
        """Test normalize command with corrupted CSV file."""
        # Create corrupted CSV
        corrupted_data = """time,type,base-asset,quantity
2024-01-01T00:00:00,buy,"BTC,1.0
invalid,csv,"format"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(corrupted_data)
            input_file = f.name
        
        try:
            args = MagicMock()
            args.input_file = input_file
            args.exchange = 'binance'
            args.output = 'output.csv'
            args.fetch_prices = False
            args.remove_duplicates = False
            args.sheet = None
            
            # Should handle error gracefully
            with pytest.raises((Exception, SystemExit)):
                cmd_normalize(args)
                
        finally:
            os.unlink(input_file)
    
    def test_calculate_with_invalid_method(self):
        """Test calculate command with invalid method."""
        # Create valid normalized data
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,1.0,USD,50000.0,25.0,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            args = MagicMock()
            args.input_file = input_file
            args.method = 'invalid_method'
            args.currency = 'usd'
            args.output = 'output.csv'
            
            with pytest.raises((Exception, SystemExit)):
                cmd_calculate(args)
                
        finally:
            os.unlink(input_file)
    
    def test_validate_with_empty_file(self):
        """Test validate command with empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("")  # Empty file
            input_file = f.name
        
        try:
            args = MagicMock()
            args.input_file = input_file
            
            # Should handle empty file gracefully
            cmd_validate(args)  # May succeed with warnings or fail gracefully
            
        finally:
            os.unlink(input_file)


class TestCLIArgumentParsing:
    """Test CLI argument parsing and validation."""
    
    def test_normalize_required_arguments(self):
        """Test that normalize command requires input file and exchange."""
        result = subprocess.run([
            sys.executable, 'src/main.py', 'normalize'
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        
        assert result.returncode != 0
        # Should indicate missing required arguments
        assert 'required' in result.stderr.lower() or 'error' in result.stderr.lower()
    
    def test_calculate_required_arguments(self):
        """Test that calculate command requires input file."""
        result = subprocess.run([
            sys.executable, 'src/main.py', 'calculate'
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        
        assert result.returncode != 0
        assert 'required' in result.stderr.lower() or 'error' in result.stderr.lower()
    
    def test_normalize_optional_arguments(self):
        """Test normalize command with optional arguments."""
        # Create dummy file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("time,type,base-asset,quantity,quote-asset,total\n")
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            result = subprocess.run([
                sys.executable, 'src/main.py', 'normalize',
                input_file, 'binance',
                '--output', output_file,
                '--fetch-prices',
                '--remove-duplicates'
            ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
            
            # Should accept optional arguments
            # May fail due to missing data, but should parse arguments correctly
            assert 'unrecognized arguments' not in result.stderr.lower()
            
        finally:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)


class TestCLIOutputFormatting:
    """Test CLI output formatting and user feedback."""
    
    @patch('main.auto_process_input_folder')
    def test_auto_process_success_output(self, mock_auto_process):
        """Test auto-process success output formatting."""
        mock_auto_process.return_value = [
            {
                'input_file': 'test.csv',
                'output_file': 'test_normalized.csv',
                'exchange_used': 'binance',
                'detection_confidence': 0.95,
                'status': 'success'
            }
        ]
        
        args = MagicMock()
        args.input_dir = 'input'
        args.output_dir = 'output'
        args.no_interactive = True
        
        # Capture output
        with patch('builtins.print') as mock_print:
            cmd_auto_process(args)
            
            # Should print success messages
            mock_print.assert_called()
            
            # Check for success indicators in print calls
            print_calls = [str(call) for call in mock_print.call_args_list]
            success_found = any('success' in call.lower() or 'complete' in call.lower() 
                             for call in print_calls)
            assert success_found
    
    @patch('main.auto_process_input_folder')
    def test_auto_process_error_output(self, mock_auto_process):
        """Test auto-process error output formatting."""
        mock_auto_process.return_value = [
            {
                'input_file': 'test.csv',
                'exchange_used': 'binance',
                'detection_confidence': 0.95,
                'status': 'error',
                'error': 'File format not supported'
            }
        ]
        
        args = MagicMock()
        args.input_dir = 'input'
        args.output_dir = 'output'
        args.no_interactive = True
        
        with patch('builtins.print') as mock_print:
            cmd_auto_process(args)
            
            # Should print error messages
            print_calls = [str(call) for call in mock_print.call_args_list]
            error_found = any('error' in call.lower() or 'failed' in call.lower() 
                            for call in print_calls)
            assert error_found


class TestCLIPerformance:
    """Test CLI performance with various scenarios."""
    
    def test_large_file_processing(self):
        """Test CLI performance with large files."""
        # Generate large test file
        rows = []
        for i in range(1000):
            rows.append(f"2024-01-{(i % 30) + 1:02d}T00:00:00,buy,BTC,{0.001 * (i + 1):.6f},USDT,{50000 + i:.2f},25.0,USDT")
        
        test_data = "time,type,base-asset,quantity,quote-asset,total,fee,fee-currency\n" + "\n".join(rows)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            import time
            start_time = time.time()
            
            args = MagicMock()
            args.input_file = input_file
            args.exchange = 'binance'
            args.output = output_file
            args.fetch_prices = False
            args.remove_duplicates = False
            args.sheet = None
            
            cmd_normalize(args)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Should complete within reasonable time
            assert processing_time < 30  # Adjust threshold as needed
            assert os.path.exists(output_file)
            
        finally:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])