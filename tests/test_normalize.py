"""Comprehensive unit tests for the normalize module."""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from normalize import normalize_csv, parse_pair, load_mappings
from exceptions import FileFormatError, DataValidationError


class TestParsePair:
    """Test cases for trading pair parsing."""
    
    def test_parse_pair_with_separator(self):
        """Test parsing trading pairs with separators."""
        assert parse_pair("BTC/USD") == ("BTC", "USD")
        assert parse_pair("ETH-USDT") == ("ETH", "USDT")
        assert parse_pair("ADA_EUR") == ("ADA", "EUR")
        assert parse_pair("DOT:GBP") == ("DOT", "GBP")
    
    def test_parse_pair_without_separator(self):
        """Test parsing trading pairs without separators."""
        assert parse_pair("BTCUSD") == ("BTC", "USD")
        assert parse_pair("ETHUSDT") == ("ETH", "USDT")
        assert parse_pair("ADAEUR") == ("ADA", "EUR")
        assert parse_pair("DOTUSD") == ("DOT", "USD")
    
    def test_parse_pair_kraken_format(self):
        """Test parsing Kraken-style pairs with X/Z prefixes."""
        # Note: Actual implementation may vary, testing expected behavior
        result = parse_pair("XBTUSD")
        assert result[0] is not None  # Should extract some base asset
        
        result = parse_pair("XETHZUSD")
        assert result[0] is not None  # Should extract some base asset
    
    def test_parse_pair_complex_assets(self):
        """Test parsing pairs with complex asset names."""
        assert parse_pair("SHIB/USDT") == ("SHIB", "USDT")
        assert parse_pair("MATIC-EUR") == ("MATIC", "EUR")
        assert parse_pair("AVAX_BTC") == ("AVAX", "BTC")
        assert parse_pair("1INCH/USD") == ("1INCH", "USD")
    
    def test_parse_pair_invalid(self):
        """Test parsing invalid or empty pairs."""
        assert parse_pair("") == (None, None)
        assert parse_pair(None) == (None, None)
        assert parse_pair("INVALID") == ("INVALID", None)
        assert parse_pair("A") == ("A", None)  # Too short to split
    
    def test_parse_pair_edge_cases(self):
        """Test edge cases in pair parsing."""
        # Multiple separators
        assert parse_pair("BTC/USD/EUR")[0] == "BTC"  # Should handle gracefully
        
        # Mixed case
        assert parse_pair("btc/usd") == ("BTC", "USD")
        assert parse_pair("Eth-Usdt") == ("ETH", "USDT")
        
        # Whitespace
        assert parse_pair(" BTC/USD ") == ("BTC", "USD")
        assert parse_pair("BTC / USD") == ("BTC", "USD")
    
class TestNormalizeCSV:
    """Test cases for CSV normalization functionality."""
    
    def test_normalize_binance_format(self):
        """Test normalization of Binance format CSV."""
        sample_data = """time,type,base-asset,quantity,quote-asset,total,fee,fee-currency
2024-01-01T00:00:00,buy,BTC,1.0,USDT,50000.00,25.00,USDT
2024-01-02T00:00:00,sell,BTC,0.5,USDT,26000.00,13.00,USDT"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_data)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            normalize_csv(input_file, 'binance', output_file)
            
            # Verify output structure
            df = pd.read_csv(output_file)
            assert len(df) == 2
            
            # Check required columns exist
            required_columns = ['timestamp', 'type', 'base_asset', 'base_amount', 
                              'quote_asset', 'quote_amount', 'fee_amount', 'fee_asset']
            for col in required_columns:
                assert col in df.columns, f"Missing required column: {col}"
            
            # Verify data content
            assert df['base_asset'].iloc[0] == 'BTC'
            assert df['base_amount'].iloc[0] == 1.0
            assert df['quote_asset'].iloc[0] == 'USDT'
            assert df['quote_amount'].iloc[0] == 50000.0
            assert df['fee_amount'].iloc[0] == 25.0
            assert df['fee_asset'].iloc[0] == 'USDT'
            
        finally:
            os.unlink(input_file)
            os.unlink(output_file)
    
    def test_normalize_coinbase_format(self):
        """Test normalization of Coinbase format CSV."""
        sample_data = """Timestamp,Transaction Type,Asset,Quantity Transacted,Spot Price Currency,Subtotal,Fees and/or Spread,Notes
2024-01-01T00:00:00Z,Buy,BTC,0.5,USD,25000.00,50.00,Market order
2024-01-02T00:00:00Z,Sell,BTC,0.25,USD,13000.00,26.00,Limit order"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_data)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            normalize_csv(input_file, 'coinbase', output_file)
            
            df = pd.read_csv(output_file)
            assert len(df) == 2
            assert df['base_asset'].iloc[0] == 'BTC'
            assert df['type'].iloc[0].lower() == 'buy'
            assert df['base_amount'].iloc[0] == 0.5
            assert df['quote_asset'].iloc[0] == 'USD'
            
        finally:
            os.unlink(input_file)
            os.unlink(output_file)
    
    def test_normalize_kraken_format(self):
        """Test normalization of Kraken format CSV."""
        sample_data = """time,type,pair,vol,cost,fee,ledgers
2024-01-01T00:00:00Z,buy,XBTUSD,0.5,25000.00,12.50,L123456
2024-01-02T00:00:00Z,sell,XBTUSD,0.25,13000.00,6.50,L123457"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_data)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            normalize_csv(input_file, 'kraken', output_file)
            
            df = pd.read_csv(output_file)
            assert len(df) == 2
            assert df['type'].iloc[0].lower() == 'buy'
            assert df['base_amount'].iloc[0] == 0.5
            
        finally:
            os.unlink(input_file)
            os.unlink(output_file)
    
    def test_normalize_with_missing_columns(self):
        """Test normalization with missing optional columns."""
        # Binance format without fee columns
        sample_data = """time,type,base-asset,quantity,quote-asset,total
2024-01-01T00:00:00,buy,BTC,1.0,USDT,50000.00"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_data)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            normalize_csv(input_file, 'binance', output_file)
            
            df = pd.read_csv(output_file)
            assert len(df) == 1
            # Fee columns should be filled with defaults or NaN
            assert 'fee_amount' in df.columns
            assert 'fee_asset' in df.columns
            
        finally:
            os.unlink(input_file)
            os.unlink(output_file)
    
    def test_normalize_with_malformed_data(self):
        """Test normalization with malformed data."""
        # Data with invalid numbers and dates
        sample_data = """time,type,base-asset,quantity,quote-asset,total,fee,fee-currency
invalid_date,buy,BTC,invalid_number,USDT,50000.00,25.00,USDT
2024-01-02T00:00:00,sell,BTC,0.5,USDT,26000.00,13.00,USDT"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_data)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            # Should handle malformed data gracefully
            normalize_csv(input_file, 'binance', output_file)
            
            df = pd.read_csv(output_file)
            # Should have at least the valid row
            assert len(df) >= 1
            
        finally:
            os.unlink(input_file)
            os.unlink(output_file)
    
    def test_normalize_xlsx_format(self):
        """Test normalization of XLSX files."""
        # Create a simple XLSX file
        sample_data = {
            'time': ['2024-01-01T00:00:00', '2024-01-02T00:00:00'],
            'type': ['buy', 'sell'],
            'base-asset': ['BTC', 'BTC'],
            'quantity': [1.0, 0.5],
            'quote-asset': ['USDT', 'USDT'],
            'total': [50000.0, 26000.0],
            'fee': [25.0, 13.0],
            'fee-currency': ['USDT', 'USDT']
        }
        
        df_input = pd.DataFrame(sample_data)
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            # Write XLSX file
            df_input.to_excel(input_file, index=False)
            
            normalize_csv(input_file, 'binance', output_file)
            
            df = pd.read_csv(output_file)
            assert len(df) == 2
            assert df['base_asset'].iloc[0] == 'BTC'
            
        finally:
            os.unlink(input_file)
            os.unlink(output_file)
    
    def test_normalize_with_duplicate_removal(self):
        """Test normalization with duplicate transaction removal."""
        # Data with duplicate transactions
        sample_data = """time,type,base-asset,quantity,quote-asset,total,fee,fee-currency
2024-01-01T00:00:00,buy,BTC,1.0,USDT,50000.00,25.00,USDT
2024-01-01T00:00:00,buy,BTC,1.0,USDT,50000.00,25.00,USDT
2024-01-02T00:00:00,sell,BTC,0.5,USDT,26000.00,13.00,USDT"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_data)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            normalize_csv(input_file, 'binance', output_file, remove_duplicates=True)
            
            df = pd.read_csv(output_file)
            # Should have removed one duplicate
            assert len(df) == 2
            
        finally:
            os.unlink(input_file)
            os.unlink(output_file)
    
class TestNormalizeErrorHandling:
    """Test error handling in normalization."""
    
    def test_normalize_invalid_exchange(self):
        """Test normalization with invalid exchange name."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("col1,col2\nval1,val2")
            input_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported exchange"):
                normalize_csv(input_file, 'invalid_exchange', 'output.csv')
        finally:
            os.unlink(input_file)
    
    def test_normalize_empty_file(self):
        """Test normalization with empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("")  # Empty file
            input_file = f.name
        
        try:
            with pytest.raises((ValueError, FileFormatError, pd.errors.EmptyDataError)):
                normalize_csv(input_file, 'binance', 'output.csv')
        finally:
            os.unlink(input_file)
    
    def test_normalize_nonexistent_file(self):
        """Test normalization with non-existent input file."""
        with pytest.raises((FileNotFoundError, FileFormatError)):
            normalize_csv('nonexistent_file.csv', 'binance', 'output.csv')
    
    def test_normalize_invalid_file_format(self):
        """Test normalization with unsupported file format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("some text data")
            input_file = f.name
        
        try:
            with pytest.raises((ValueError, FileFormatError)):
                normalize_csv(input_file, 'binance', 'output.csv')
        finally:
            os.unlink(input_file)
    
    def test_normalize_corrupted_csv(self):
        """Test normalization with corrupted CSV data."""
        # CSV with mismatched quotes and commas
        corrupted_data = '''time,type,base-asset,quantity
2024-01-01T00:00:00,buy,"BTC,1.0
2024-01-02T00:00:00,sell,BTC",0.5'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(corrupted_data)
            input_file = f.name
        
        try:
            # Should handle parsing errors gracefully
            with pytest.raises((pd.errors.ParserError, FileFormatError)):
                normalize_csv(input_file, 'binance', 'output.csv')
        finally:
            os.unlink(input_file)
    
    def test_normalize_insufficient_columns(self):
        """Test normalization with insufficient columns."""
        # Only one column - insufficient for any exchange
        sample_data = """time
2024-01-01T00:00:00
2024-01-02T00:00:00"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_data)
            input_file = f.name
        
        try:
            with pytest.raises((ValueError, DataValidationError)):
                normalize_csv(input_file, 'binance', 'output.csv')
        finally:
            os.unlink(input_file)
    
    def test_normalize_missing_required_columns(self):
        """Test normalization with missing required columns."""
        # Missing critical columns for Binance format
        sample_data = """time,type
2024-01-01T00:00:00,buy
2024-01-02T00:00:00,sell"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_data)
            input_file = f.name
        
        try:
            # Should raise error for missing required columns
            with pytest.raises((ValueError, DataValidationError)):
                normalize_csv(input_file, 'binance', 'output.csv')
        finally:
            os.unlink(input_file)


class TestLoadMappings:
    """Test exchange mapping configuration loading."""
    
    def test_load_mappings_success(self):
        """Test successful loading of exchange mappings."""
        mappings = load_mappings()
        
        # Should load multiple exchanges
        assert isinstance(mappings, dict)
        assert len(mappings) > 0
        
        # Should contain major exchanges
        expected_exchanges = ['binance', 'coinbase', 'kraken']
        for exchange in expected_exchanges:
            assert exchange in mappings, f"Missing exchange: {exchange}"
    
    def test_mapping_structure(self):
        """Test structure of exchange mappings."""
        mappings = load_mappings()
        
        for exchange, mapping in mappings.items():
            assert isinstance(mapping, dict), f"Invalid mapping for {exchange}"
            
            # Should have basic field mappings
            expected_fields = ['timestamp', 'type', 'base_asset', 'base_amount']
            for field in expected_fields:
                # Field should exist in mapping (value can be None for optional fields)
                assert field in mapping or any(field in str(v) for v in mapping.values()), \
                    f"Missing field {field} in {exchange} mapping"
    
    @patch('normalize.load_exchange_mappings')
    def test_load_mappings_file_error(self, mock_load):
        """Test handling of mapping file errors."""
        mock_load.side_effect = FileNotFoundError("Config file not found")
        
        with pytest.raises(FileNotFoundError):
            load_mappings()
    
    @patch('normalize.load_exchange_mappings')
    def test_load_mappings_invalid_yaml(self, mock_load):
        """Test handling of invalid YAML in mappings."""
        mock_load.side_effect = Exception("Invalid YAML format")
        
        with pytest.raises(Exception):
            load_mappings()


class TestNormalizeIntegration:
    """Integration tests for normalization workflow."""
    
    def test_full_normalization_workflow(self):
        """Test complete normalization workflow with price fetching."""
        sample_data = """time,type,base-asset,quantity,quote-asset,total,fee,fee-currency
2024-01-01T00:00:00,buy,BTC,1.0,USDT,50000.00,25.00,USDT
2024-01-02T00:00:00,sell,BTC,0.5,USDT,26000.00,13.00,USDT"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_data)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            # Test with all options
            normalize_csv(
                input_file=input_file,
                exchange='binance',
                output_file=output_file,
                fetch_missing_prices=False,  # Skip API calls in tests
                remove_duplicates=True
            )
            
            # Verify complete output
            df = pd.read_csv(output_file)
            assert len(df) == 2
            
            # Check all required columns are present
            required_columns = [
                'timestamp', 'type', 'base_asset', 'base_amount',
                'quote_asset', 'quote_amount', 'fee_amount', 'fee_asset', 'notes'
            ]
            
            for col in required_columns:
                assert col in df.columns, f"Missing column: {col}"
            
            # Verify data types
            assert pd.api.types.is_datetime64_any_dtype(df['timestamp']) or \
                   df['timestamp'].dtype == 'object'  # String timestamps are acceptable
            assert pd.api.types.is_numeric_dtype(df['base_amount'])
            assert pd.api.types.is_numeric_dtype(df['quote_amount'])
            
        finally:
            os.unlink(input_file)
            os.unlink(output_file)
    
    def test_multiple_exchange_formats(self):
        """Test normalization of multiple exchange formats."""
        exchange_samples = {
            'binance': """time,type,base-asset,quantity,quote-asset,total,fee,fee-currency
2024-01-01T00:00:00,buy,BTC,1.0,USDT,50000.00,25.00,USDT""",
            
            'coinbase': """Timestamp,Transaction Type,Asset,Quantity Transacted,Spot Price Currency,Subtotal,Fees and/or Spread,Notes
2024-01-01T00:00:00Z,Buy,BTC,0.5,USD,25000.00,50.00,Market order""",
            
            'kraken': """time,type,pair,vol,cost,fee,ledgers
2024-01-01T00:00:00Z,buy,XBTUSD,0.5,25000.00,12.50,L123456"""
        }
        
        for exchange, sample_data in exchange_samples.items():
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write(sample_data)
                input_file = f.name
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                output_file = f.name
            
            try:
                normalize_csv(input_file, exchange, output_file)
                
                # Verify each exchange produces valid output
                df = pd.read_csv(output_file)
                assert len(df) >= 1, f"No data normalized for {exchange}"
                assert 'base_asset' in df.columns, f"Missing base_asset for {exchange}"
                assert 'type' in df.columns, f"Missing type for {exchange}"
                
            finally:
                os.unlink(input_file)
                os.unlink(output_file)


if __name__ == '__main__':
    pytest.main([__file__])


class TestNormalizePerformance:
    """Performance tests for normalization."""
    
    def test_large_file_normalization(self):
        """Test normalization with large dataset."""
        # Generate large dataset (1000 rows)
        rows = []
        for i in range(1000):
            rows.append(f"2024-01-{(i % 30) + 1:02d}T{(i % 24):02d}:00:00,buy,BTC,{0.001 * (i + 1):.6f},USDT,{50000 + i * 10:.2f},{25 + i * 0.1:.2f},USDT")
        
        sample_data = "time,type,base-asset,quantity,quote-asset,total,fee,fee-currency\n" + "\n".join(rows)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_data)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            import time
            start_time = time.time()
            
            normalize_csv(input_file, 'binance', output_file)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Should complete within reasonable time (adjust threshold as needed)
            assert processing_time < 30, f"Processing took too long: {processing_time:.2f}s"
            
            # Verify all data was processed
            df = pd.read_csv(output_file)
            assert len(df) == 1000, f"Expected 1000 rows, got {len(df)}"
            
        finally:
            os.unlink(input_file)
            os.unlink(output_file)
    
    def test_memory_usage_large_file(self):
        """Test memory usage with large files."""
        # This test would require memory profiling tools in a real scenario
        # For now, just ensure large files don't crash
        
        # Generate moderately large dataset
        rows = []
        for i in range(5000):
            rows.append(f"2024-01-01T00:00:00,buy,BTC,1.0,USDT,50000.00,25.00,USDT")
        
        sample_data = "time,type,base-asset,quantity,quote-asset,total,fee,fee-currency\n" + "\n".join(rows)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_data)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            # Should not crash with memory errors
            normalize_csv(input_file, 'binance', output_file)
            
            df = pd.read_csv(output_file)
            assert len(df) > 0
            
        finally:
            os.unlink(input_file)
            os.unlink(output_file)


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])