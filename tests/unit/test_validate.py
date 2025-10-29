"""Comprehensive unit tests for the validate module."""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from validate import validate_df, check_required_fields, check_duplicates, check_balances
from exceptions import DataValidationError


class TestValidateDF:
    """Test cases for main validation function."""
    
    def test_validate_valid_dataframe(self):
        """Test validation of a valid normalized dataframe."""
        # Create valid sample data
        data = {
            'timestamp': ['2024-01-01T00:00:00', '2024-01-02T00:00:00'],
            'type': ['buy', 'sell'],
            'base_asset': ['BTC', 'BTC'],
            'base_amount': [1.0, 0.5],
            'quote_asset': ['USD', 'USD'],
            'quote_amount': [50000.0, 26000.0],
            'fee_amount': [25.0, 13.0],
            'fee_asset': ['USD', 'USD'],
            'notes': ['', '']
        }
        
        df = pd.DataFrame(data)
        
        # Should pass validation without errors
        result = validate_df(df)
        
        assert result['is_valid'] == True
        assert len(result['errors']) == 0
        assert len(result['warnings']) == 0
        assert result['total_transactions'] == 2
    
    def test_validate_missing_required_columns(self):
        """Test validation with missing required columns."""
        # Missing base_asset column
        data = {
            'timestamp': ['2024-01-01T00:00:00'],
            'type': ['buy'],
            'base_amount': [1.0],
            'quote_asset': ['USD'],
            'quote_amount': [50000.0]
        }
        
        df = pd.DataFrame(data)
        
        result = validate_df(df)
        
        assert result['is_valid'] == False
        assert len(result['errors']) > 0
        assert any('base_asset' in error for error in result['errors'])
    
    def test_validate_invalid_transaction_types(self):
        """Test validation with invalid transaction types."""
        data = {
            'timestamp': ['2024-01-01T00:00:00', '2024-01-02T00:00:00'],
            'type': ['buy', 'invalid_type'],
            'base_asset': ['BTC', 'BTC'],
            'base_amount': [1.0, 0.5],
            'quote_asset': ['USD', 'USD'],
            'quote_amount': [50000.0, 26000.0],
            'fee_amount': [25.0, 13.0],
            'fee_asset': ['USD', 'USD'],
            'notes': ['', '']
        }
        
        df = pd.DataFrame(data)
        
        result = validate_df(df)
        
        assert result['is_valid'] == False
        assert len(result['errors']) > 0
        assert any('invalid_type' in str(error) for error in result['errors'])
    
    def test_validate_negative_amounts(self):
        """Test validation with negative amounts."""
        data = {
            'timestamp': ['2024-01-01T00:00:00', '2024-01-02T00:00:00'],
            'type': ['buy', 'sell'],
            'base_asset': ['BTC', 'BTC'],
            'base_amount': [-1.0, 0.5],  # Negative amount
            'quote_asset': ['USD', 'USD'],
            'quote_amount': [50000.0, -26000.0],  # Negative amount
            'fee_amount': [25.0, 13.0],
            'fee_asset': ['USD', 'USD'],
            'notes': ['', '']
        }
        
        df = pd.DataFrame(data)
        
        result = validate_df(df)
        
        assert result['is_valid'] == False
        assert len(result['errors']) > 0
        assert any('negative' in str(error).lower() for error in result['errors'])
    
    def test_validate_duplicate_transactions(self):
        """Test validation with duplicate transactions."""
        # Identical transactions
        data = {
            'timestamp': ['2024-01-01T00:00:00', '2024-01-01T00:00:00'],
            'type': ['buy', 'buy'],
            'base_asset': ['BTC', 'BTC'],
            'base_amount': [1.0, 1.0],
            'quote_asset': ['USD', 'USD'],
            'quote_amount': [50000.0, 50000.0],
            'fee_amount': [25.0, 25.0],
            'fee_asset': ['USD', 'USD'],
            'notes': ['', '']
        }
        
        df = pd.DataFrame(data)
        
        result = validate_df(df)
        
        # Should detect duplicates (may be warning or error depending on implementation)
        assert len(result['duplicates']) > 0 or len(result['warnings']) > 0
    
    def test_validate_invalid_timestamps(self):
        """Test validation with invalid timestamp formats."""
        data = {
            'timestamp': ['invalid_date', '2024-01-02T00:00:00'],
            'type': ['buy', 'sell'],
            'base_asset': ['BTC', 'BTC'],
            'base_amount': [1.0, 0.5],
            'quote_asset': ['USD', 'USD'],
            'quote_amount': [50000.0, 26000.0],
            'fee_amount': [25.0, 13.0],
            'fee_asset': ['USD', 'USD'],
            'notes': ['', '']
        }
        
        df = pd.DataFrame(data)
        
        result = validate_df(df)
        
        assert result['is_valid'] == False
        assert len(result['errors']) > 0
        assert any('timestamp' in str(error).lower() or 'date' in str(error).lower() 
                  for error in result['errors'])


class TestCheckRequiredFields:
    """Test cases for required field validation."""
    
    def test_check_required_fields_all_present(self):
        """Test when all required fields are present."""
        data = {
            'timestamp': ['2024-01-01T00:00:00'],
            'type': ['buy'],
            'base_asset': ['BTC'],
            'base_amount': [1.0],
            'quote_asset': ['USD'],
            'quote_amount': [50000.0],
            'fee_amount': [25.0],
            'fee_asset': ['USD'],
            'notes': ['']
        }
        
        df = pd.DataFrame(data)
        
        errors = check_required_fields(df)
        assert len(errors) == 0
    
    def test_check_required_fields_missing_columns(self):
        """Test when required columns are missing."""
        data = {
            'timestamp': ['2024-01-01T00:00:00'],
            'type': ['buy'],
            # Missing base_asset, base_amount, etc.
        }
        
        df = pd.DataFrame(data)
        
        errors = check_required_fields(df)
        assert len(errors) > 0
        
        # Should identify specific missing columns
        missing_fields = ['base_asset', 'base_amount', 'quote_asset', 'quote_amount']
        for field in missing_fields:
            assert any(field in str(error) for error in errors)
    
    def test_check_required_fields_empty_values(self):
        """Test when required fields have empty/null values."""
        data = {
            'timestamp': ['2024-01-01T00:00:00', ''],
            'type': ['buy', None],
            'base_asset': ['BTC', ''],
            'base_amount': [1.0, None],
            'quote_asset': ['USD', 'USD'],
            'quote_amount': [50000.0, 26000.0],
            'fee_amount': [25.0, 13.0],
            'fee_asset': ['USD', 'USD'],
            'notes': ['', '']
        }
        
        df = pd.DataFrame(data)
        
        errors = check_required_fields(df)
        assert len(errors) > 0
        
        # Should identify rows with empty required values
        assert any('empty' in str(error).lower() or 'null' in str(error).lower() 
                  for error in errors)


class TestCheckDuplicates:
    """Test cases for duplicate detection."""
    
    def test_check_duplicates_none_found(self):
        """Test when no duplicates exist."""
        data = {
            'timestamp': ['2024-01-01T00:00:00', '2024-01-02T00:00:00'],
            'type': ['buy', 'sell'],
            'base_asset': ['BTC', 'BTC'],
            'base_amount': [1.0, 0.5],
            'quote_asset': ['USD', 'USD'],
            'quote_amount': [50000.0, 26000.0]
        }
        
        df = pd.DataFrame(data)
        
        duplicates = check_duplicates(df)
        assert len(duplicates) == 0
    
    def test_check_duplicates_exact_matches(self):
        """Test detection of exact duplicate transactions."""
        data = {
            'timestamp': ['2024-01-01T00:00:00', '2024-01-01T00:00:00', '2024-01-02T00:00:00'],
            'type': ['buy', 'buy', 'sell'],
            'base_asset': ['BTC', 'BTC', 'BTC'],
            'base_amount': [1.0, 1.0, 0.5],
            'quote_asset': ['USD', 'USD', 'USD'],
            'quote_amount': [50000.0, 50000.0, 26000.0]
        }
        
        df = pd.DataFrame(data)
        
        duplicates = check_duplicates(df)
        assert len(duplicates) > 0
        
        # Should identify the duplicate rows
        assert any(0 in dup_group or 1 in dup_group for dup_group in duplicates)
    
    def test_check_duplicates_partial_matches(self):
        """Test detection of partial duplicates (same key fields)."""
        data = {
            'timestamp': ['2024-01-01T00:00:00', '2024-01-01T00:00:00'],
            'type': ['buy', 'buy'],
            'base_asset': ['BTC', 'BTC'],
            'base_amount': [1.0, 1.0],
            'quote_asset': ['USD', 'USD'],
            'quote_amount': [50000.0, 50001.0],  # Slightly different amount
            'notes': ['note1', 'note2']  # Different notes
        }
        
        df = pd.DataFrame(data)
        
        duplicates = check_duplicates(df)
        # Behavior depends on implementation - may or may not detect as duplicates
        # This test documents the expected behavior
        assert isinstance(duplicates, list)
    
    def test_check_duplicates_multiple_groups(self):
        """Test detection of multiple duplicate groups."""
        data = {
            'timestamp': ['2024-01-01T00:00:00', '2024-01-01T00:00:00', 
                         '2024-01-02T00:00:00', '2024-01-02T00:00:00',
                         '2024-01-03T00:00:00'],
            'type': ['buy', 'buy', 'sell', 'sell', 'buy'],
            'base_asset': ['BTC', 'BTC', 'BTC', 'BTC', 'ETH'],
            'base_amount': [1.0, 1.0, 0.5, 0.5, 2.0],
            'quote_asset': ['USD', 'USD', 'USD', 'USD', 'USD'],
            'quote_amount': [50000.0, 50000.0, 26000.0, 26000.0, 6000.0]
        }
        
        df = pd.DataFrame(data)
        
        duplicates = check_duplicates(df)
        
        # Should find two groups of duplicates
        assert len(duplicates) >= 2


class TestCheckBalances:
    """Test cases for balance validation."""
    
    def test_check_balances_valid_sequence(self):
        """Test balance checking with valid transaction sequence."""
        data = {
            'timestamp': ['2024-01-01T00:00:00', '2024-01-02T00:00:00', '2024-01-03T00:00:00'],
            'type': ['deposit', 'buy', 'sell'],
            'base_asset': ['BTC', 'BTC', 'BTC'],
            'base_amount': [1.0, 0.5, 0.3],
            'quote_asset': ['', 'USD', 'USD'],
            'quote_amount': [0.0, 25000.0, 15000.0]
        }
        
        df = pd.DataFrame(data)
        
        negative_balances = check_balances(df)
        
        # Should not have negative balances with this sequence
        assert len(negative_balances) == 0
    
    def test_check_balances_negative_balance(self):
        """Test balance checking with transactions causing negative balance."""
        data = {
            'timestamp': ['2024-01-01T00:00:00', '2024-01-02T00:00:00'],
            'type': ['sell', 'buy'],  # Selling before buying
            'base_asset': ['BTC', 'BTC'],
            'base_amount': [1.0, 0.5],
            'quote_asset': ['USD', 'USD'],
            'quote_amount': [50000.0, 25000.0]
        }
        
        df = pd.DataFrame(data)
        
        negative_balances = check_balances(df)
        
        # Should detect negative balance for BTC
        assert len(negative_balances) > 0
        assert any('BTC' in str(balance) for balance in negative_balances)
    
    def test_check_balances_multiple_assets(self):
        """Test balance checking with multiple assets."""
        data = {
            'timestamp': ['2024-01-01T00:00:00', '2024-01-02T00:00:00', 
                         '2024-01-03T00:00:00', '2024-01-04T00:00:00'],
            'type': ['deposit', 'deposit', 'sell', 'sell'],
            'base_asset': ['BTC', 'ETH', 'BTC', 'ETH'],
            'base_amount': [1.0, 10.0, 0.5, 5.0],
            'quote_asset': ['', '', 'USD', 'USD'],
            'quote_amount': [0.0, 0.0, 25000.0, 15000.0]
        }
        
        df = pd.DataFrame(data)
        
        negative_balances = check_balances(df)
        
        # Should not have negative balances
        assert len(negative_balances) == 0
    
    def test_check_balances_complex_sequence(self):
        """Test balance checking with complex transaction sequence."""
        data = {
            'timestamp': ['2024-01-01T00:00:00', '2024-01-02T00:00:00', 
                         '2024-01-03T00:00:00', '2024-01-04T00:00:00',
                         '2024-01-05T00:00:00'],
            'type': ['deposit', 'buy', 'sell', 'withdraw', 'sell'],
            'base_asset': ['USD', 'BTC', 'BTC', 'USD', 'BTC'],
            'base_amount': [100000.0, 1.0, 0.5, 50000.0, 0.6],  # Last sell exceeds balance
            'quote_asset': ['', 'USD', 'USD', '', 'USD'],
            'quote_amount': [0.0, 50000.0, 26000.0, 0.0, 30000.0]
        }
        
        df = pd.DataFrame(data)
        
        negative_balances = check_balances(df)
        
        # Should detect negative balance for BTC (selling 0.6 when only 0.5 remains)
        assert len(negative_balances) > 0


class TestValidationIntegration:
    """Integration tests for validation workflow."""
    
    def test_validate_real_world_data(self):
        """Test validation with realistic transaction data."""
        # Simulate real-world trading data
        data = {
            'timestamp': [
                '2024-01-01T09:00:00', '2024-01-01T10:30:00', '2024-01-02T14:15:00',
                '2024-01-03T11:45:00', '2024-01-04T16:20:00'
            ],
            'type': ['deposit', 'buy', 'sell', 'buy', 'withdraw'],
            'base_asset': ['USD', 'BTC', 'BTC', 'ETH', 'ETH'],
            'base_amount': [10000.0, 0.2, 0.1, 5.0, 2.0],
            'quote_asset': ['', 'USD', 'USD', 'USD', ''],
            'quote_amount': [0.0, 8000.0, 4200.0, 15000.0, 0.0],
            'fee_amount': [0.0, 8.0, 4.2, 15.0, 0.0],
            'fee_asset': ['', 'USD', 'USD', 'USD', ''],
            'notes': ['Bank transfer', 'Market buy', 'Limit sell', 'Market buy', 'To wallet']
        }
        
        df = pd.DataFrame(data)
        
        result = validate_df(df)
        
        # Should pass validation
        assert result['is_valid'] == True
        assert result['total_transactions'] == 5
        assert len(result['errors']) == 0
        
        # Should have reasonable statistics
        assert result['unique_assets'] >= 2  # USD, BTC, ETH
        assert result['date_range']['start'] is not None
        assert result['date_range']['end'] is not None
    
    def test_validate_edge_cases(self):
        """Test validation with edge cases."""
        # Very small amounts, unusual assets, etc.
        data = {
            'timestamp': ['2024-01-01T00:00:00', '2024-01-02T00:00:00'],
            'type': ['buy', 'sell'],
            'base_asset': ['SHIB', 'SHIB'],  # Meme coin with large supply
            'base_amount': [1000000.0, 500000.0],  # Large amounts
            'quote_asset': ['USD', 'USD'],
            'quote_amount': [10.0, 5.5],  # Small USD amounts
            'fee_amount': [0.01, 0.005],  # Very small fees
            'fee_asset': ['USD', 'USD'],
            'notes': ['', '']
        }
        
        df = pd.DataFrame(data)
        
        result = validate_df(df)
        
        # Should handle edge cases gracefully
        assert isinstance(result, dict)
        assert 'is_valid' in result
        assert 'errors' in result
        assert 'warnings' in result
    
    def test_validate_empty_dataframe(self):
        """Test validation with empty dataframe."""
        df = pd.DataFrame()
        
        result = validate_df(df)
        
        assert result['is_valid'] == False
        assert len(result['errors']) > 0
        assert result['total_transactions'] == 0
    
    def test_validate_single_transaction(self):
        """Test validation with single transaction."""
        data = {
            'timestamp': ['2024-01-01T00:00:00'],
            'type': ['deposit'],
            'base_asset': ['BTC'],
            'base_amount': [1.0],
            'quote_asset': [''],
            'quote_amount': [0.0],
            'fee_amount': [0.0],
            'fee_asset': [''],
            'notes': ['Initial deposit']
        }
        
        df = pd.DataFrame(data)
        
        result = validate_df(df)
        
        assert result['is_valid'] == True
        assert result['total_transactions'] == 1
        assert len(result['errors']) == 0


class TestValidationErrorHandling:
    """Test error handling in validation functions."""
    
    def test_validate_invalid_dataframe_type(self):
        """Test validation with invalid input type."""
        with pytest.raises((TypeError, AttributeError)):
            validate_df("not a dataframe")
    
    def test_validate_corrupted_data(self):
        """Test validation with corrupted data types."""
        data = {
            'timestamp': [123, 'invalid'],  # Mixed types
            'type': ['buy', 456],  # Mixed types
            'base_asset': ['BTC', None],
            'base_amount': ['not_a_number', 1.0],  # Mixed types
            'quote_asset': ['USD', 'USD'],
            'quote_amount': [50000.0, 'invalid']  # Mixed types
        }
        
        df = pd.DataFrame(data)
        
        # Should handle corrupted data gracefully
        result = validate_df(df)
        
        assert isinstance(result, dict)
        assert result['is_valid'] == False
        assert len(result['errors']) > 0


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])