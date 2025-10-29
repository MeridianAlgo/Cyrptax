"""Comprehensive unit tests for the calculate module."""

import pytest
import pandas as pd
import tempfile
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from decimal import Decimal

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calculate import TaxLot, AssetInventory, TaxCalculator, calculate_taxes
from exceptions import TaxCalculationError


class TestTaxLot:
    """Test cases for TaxLot class."""
    
    def test_tax_lot_creation(self):
        """Test creating a tax lot."""
        date = datetime(2024, 1, 1)
        lot = TaxLot(1.0, 50000.0, date, "tx1")
        
        assert lot.amount == 1.0
        assert lot.cost_basis == 50000.0
        assert lot.acquisition_date == date
        assert lot.transaction_id == "tx1"
        assert lot.unit_cost == 50000.0
    
    def test_tax_lot_zero_amount(self):
        """Test tax lot with zero amount."""
        date = datetime(2024, 1, 1)
        lot = TaxLot(0.0, 0.0, date)
        
        assert lot.unit_cost == 0
    
    def test_tax_lot_partial_use(self):
        """Test using partial amount from tax lot."""
        date = datetime(2024, 1, 1)
        lot = TaxLot(1.0, 50000.0, date, "tx1")
        
        # Use half the lot
        partial_lot = lot.use_amount(0.5)
        
        assert partial_lot.amount == 0.5
        assert partial_lot.cost_basis == 25000.0
        assert partial_lot.unit_cost == 50000.0
        assert partial_lot.acquisition_date == date
        
        # Original lot should be reduced
        assert lot.amount == 0.5
        assert lot.cost_basis == 25000.0
    
    def test_tax_lot_use_full_amount(self):
        """Test using full amount from tax lot."""
        date = datetime(2024, 1, 1)
        lot = TaxLot(1.0, 50000.0, date, "tx1")
        
        partial_lot = lot.use_amount(1.0)
        
        assert partial_lot.amount == 1.0
        assert partial_lot.cost_basis == 50000.0
        assert lot.amount == 0.0
        assert lot.cost_basis == 0.0
    
    def test_tax_lot_use_excessive_amount(self):
        """Test using more than available amount."""
        date = datetime(2024, 1, 1)
        lot = TaxLot(1.0, 50000.0, date, "tx1")
        
        with pytest.raises((ValueError, TaxCalculationError)):
            lot.use_amount(1.5)
    
    def test_tax_lot_precision(self):
        """Test tax lot with high precision amounts."""
        date = datetime(2024, 1, 1)
        lot = TaxLot(0.00000001, 0.50, date)  # 1 satoshi worth $0.50
        
        assert lot.amount == 0.00000001
        assert lot.cost_basis == 0.50
        assert lot.unit_cost == 50000000.0  # $50M per BTC
    
    def test_tax_lot_comparison(self):
        """Test tax lot comparison for sorting."""
        date1 = datetime(2024, 1, 1)
        date2 = datetime(2024, 2, 1)
        
        lot1 = TaxLot(1.0, 40000.0, date1)  # Lower cost
        lot2 = TaxLot(1.0, 60000.0, date2)  # Higher cost
        
        # For HIFO sorting (highest cost first)
        assert lot2.unit_cost > lot1.unit_cost
        
        # For date sorting (FIFO/LIFO)
        assert lot1.acquisition_date < lot2.acquisition_date


class TestAssetInventory:
    """Test cases for AssetInventory class."""
    
    def test_fifo_inventory(self):
        """Test FIFO inventory management."""
        inventory = AssetInventory("BTC", "fifo")
        
        # Add lots
        lot1 = TaxLot(1.0, 40000.0, datetime(2024, 1, 1))
        lot2 = TaxLot(1.0, 60000.0, datetime(2024, 2, 1))
        
        inventory.add_lot(lot1)
        inventory.add_lot(lot2)
        
        assert inventory.total_amount == 2.0
        assert inventory.total_cost_basis == 100000.0
        
        # Remove amount (should use FIFO - oldest first)
        removed = inventory.remove_amount(0.5)
        
        assert len(removed) == 1
        assert removed[0][0].cost_basis == 20000.0  # Half of first lot
        assert inventory.total_amount == 1.5
    
    def test_lifo_inventory(self):
        """Test LIFO inventory management."""
        inventory = AssetInventory("BTC", "lifo")
        
        lot1 = TaxLot(1.0, 40000.0, datetime(2024, 1, 1))
        lot2 = TaxLot(1.0, 60000.0, datetime(2024, 2, 1))
        
        inventory.add_lot(lot1)
        inventory.add_lot(lot2)
        
        # Remove amount (should use LIFO - newest first)
        removed = inventory.remove_amount(0.5)
        
        assert len(removed) == 1
        assert removed[0][0].cost_basis == 30000.0  # Half of second lot
    
    def test_hifo_inventory(self):
        """Test HIFO inventory management."""
        inventory = AssetInventory("BTC", "hifo")
        
        lot1 = TaxLot(1.0, 40000.0, datetime(2024, 1, 1))  # $40k/BTC
        lot2 = TaxLot(1.0, 60000.0, datetime(2024, 2, 1))  # $60k/BTC
        
        inventory.add_lot(lot1)
        inventory.add_lot(lot2)
        
        # Remove amount (should use HIFO - highest cost first)
        removed = inventory.remove_amount(0.5)
        
        assert len(removed) == 1
        assert removed[0][0].cost_basis == 30000.0  # Half of highest cost lot
    
    def test_inventory_multiple_removals(self):
        """Test multiple removals from inventory."""
        inventory = AssetInventory("BTC", "fifo")
        
        # Add three lots
        lot1 = TaxLot(1.0, 30000.0, datetime(2024, 1, 1))
        lot2 = TaxLot(1.0, 40000.0, datetime(2024, 2, 1))
        lot3 = TaxLot(1.0, 50000.0, datetime(2024, 3, 1))
        
        inventory.add_lot(lot1)
        inventory.add_lot(lot2)
        inventory.add_lot(lot3)
        
        # First removal - should use first lot
        removed1 = inventory.remove_amount(0.5)
        assert len(removed1) == 1
        assert removed1[0][0].cost_basis == 15000.0
        
        # Second removal - should use rest of first lot + part of second
        removed2 = inventory.remove_amount(1.0)
        assert len(removed2) == 2
        assert removed2[0][0].cost_basis == 15000.0  # Rest of first lot
        assert removed2[1][0].cost_basis == 20000.0  # Half of second lot
        
        assert inventory.total_amount == 1.5  # 0.5 from lot2 + 1.0 from lot3
    
    def test_inventory_insufficient_balance(self):
        """Test removing more than available balance."""
        inventory = AssetInventory("BTC", "fifo")
        
        lot1 = TaxLot(1.0, 50000.0, datetime(2024, 1, 1))
        inventory.add_lot(lot1)
        
        # Try to remove more than available
        with pytest.raises((ValueError, TaxCalculationError)):
            inventory.remove_amount(1.5)
    
    def test_inventory_empty_removal(self):
        """Test removing from empty inventory."""
        inventory = AssetInventory("BTC", "fifo")
        
        with pytest.raises((ValueError, TaxCalculationError)):
            inventory.remove_amount(0.1)
    
    def test_inventory_zero_removal(self):
        """Test removing zero amount."""
        inventory = AssetInventory("BTC", "fifo")
        
        lot1 = TaxLot(1.0, 50000.0, datetime(2024, 1, 1))
        inventory.add_lot(lot1)
        
        removed = inventory.remove_amount(0.0)
        assert len(removed) == 0
        assert inventory.total_amount == 1.0
    
    def test_inventory_complex_hifo_scenario(self):
        """Test complex HIFO scenario with multiple lots."""
        inventory = AssetInventory("BTC", "hifo")
        
        # Add lots with different costs (not in chronological order)
        lot1 = TaxLot(1.0, 30000.0, datetime(2024, 1, 1))  # Lowest cost
        lot2 = TaxLot(1.0, 60000.0, datetime(2024, 2, 1))  # Highest cost
        lot3 = TaxLot(1.0, 45000.0, datetime(2024, 3, 1))  # Middle cost
        
        inventory.add_lot(lot1)
        inventory.add_lot(lot2)
        inventory.add_lot(lot3)
        
        # Remove 1.5 BTC - should use highest cost lots first
        removed = inventory.remove_amount(1.5)
        
        # Should use: full lot2 (1.0 @ $60k) + half of lot3 (0.5 @ $45k)
        assert len(removed) == 2
        assert removed[0][0].cost_basis == 60000.0  # Full highest cost lot
        assert removed[1][0].cost_basis == 22500.0  # Half of middle cost lot
        
        # Remaining should be: 0.5 from lot3 + 1.0 from lot1
        assert inventory.total_amount == 1.5
    
    def test_inventory_average_cost_basis(self):
        """Test average cost basis calculation."""
        inventory = AssetInventory("BTC", "fifo")
        
        lot1 = TaxLot(1.0, 40000.0, datetime(2024, 1, 1))
        lot2 = TaxLot(2.0, 100000.0, datetime(2024, 2, 1))  # $50k per BTC
        
        inventory.add_lot(lot1)
        inventory.add_lot(lot2)
        
        # Average cost should be (40000 + 100000) / (1 + 2) = $46,666.67
        avg_cost = inventory.average_cost_basis()
        assert abs(avg_cost - 46666.67) < 0.01


class TestTaxCalculator:
    """Test cases for TaxCalculator class."""
    
    def test_simple_buy_sell(self):
        """Test simple buy and sell calculation."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,1.0,USD,50000.0,25.0,USD,
2024-06-01T00:00:00,sell,BTC,0.5,USD,30000.0,15.0,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            assert len(gains_df) == 1
            assert gains_df.iloc[0]['asset'] == 'BTC'
            assert gains_df.iloc[0]['amount'] == 0.5
            assert gains_df.iloc[0]['short_term'] == True  # Less than 1 year
            
            # Check gain calculation: proceeds - cost basis
            # Cost basis: (50000 + 25) * 0.5 = 25012.50
            # Proceeds: 30000 - 15 = 29985
            # Gain: 29985 - 25012.50 = 4972.50
            expected_gain = 29985.0 - 25012.5
            assert abs(gains_df.iloc[0]['gain_loss'] - expected_gain) < 0.01
            
        finally:
            os.unlink(input_file)
    
    def test_long_term_gains(self):
        """Test long-term capital gains calculation."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2023-01-01T00:00:00,buy,BTC,1.0,USD,30000.0,15.0,USD,
2024-06-01T00:00:00,sell,BTC,0.5,USD,25000.0,12.5,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            assert len(gains_df) == 1
            assert gains_df.iloc[0]['short_term'] == False  # More than 1 year
            
        finally:
            os.unlink(input_file)
    
    def test_multiple_assets(self):
        """Test calculation with multiple different assets."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,1.0,USD,50000.0,25.0,USD,
2024-01-02T00:00:00,buy,ETH,10.0,USD,30000.0,15.0,USD,
2024-06-01T00:00:00,sell,BTC,0.5,USD,30000.0,15.0,USD,
2024-06-02T00:00:00,sell,ETH,5.0,USD,20000.0,10.0,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            assert len(gains_df) == 2
            
            # Check both assets are present
            assets = set(gains_df['asset'])
            assert 'BTC' in assets
            assert 'ETH' in assets
            
        finally:
            os.unlink(input_file)
    
    def test_fifo_vs_lifo_difference(self):
        """Test difference between FIFO and LIFO methods."""
        # Buy at different prices, then sell
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,1.0,USD,40000.0,20.0,USD,
2024-02-01T00:00:00,buy,BTC,1.0,USD,60000.0,30.0,USD,
2024-06-01T00:00:00,sell,BTC,1.0,USD,55000.0,27.5,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            # Test FIFO
            calculator_fifo = TaxCalculator('fifo', 'usd')
            gains_fifo, _ = calculator_fifo.calculate_taxes(input_file)
            
            # Test LIFO
            calculator_lifo = TaxCalculator('lifo', 'usd')
            gains_lifo, _ = calculator_lifo.calculate_taxes(input_file)
            
            # FIFO should use first lot (lower cost basis, higher gain)
            # LIFO should use last lot (higher cost basis, lower gain)
            assert gains_fifo.iloc[0]['gain_loss'] > gains_lifo.iloc[0]['gain_loss']
            
        finally:
            os.unlink(input_file)
    
    def test_hifo_optimization(self):
        """Test HIFO method for tax optimization."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,1.0,USD,30000.0,15.0,USD,
2024-02-01T00:00:00,buy,BTC,1.0,USD,70000.0,35.0,USD,
2024-03-01T00:00:00,buy,BTC,1.0,USD,50000.0,25.0,USD,
2024-06-01T00:00:00,sell,BTC,1.0,USD,55000.0,27.5,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('hifo', 'usd')
            gains_df, _ = calculator.calculate_taxes(input_file)
            
            # HIFO should use the highest cost lot ($70k + $35 fee)
            # This should result in a loss: 54972.5 - 70035 = -15062.5
            assert gains_df.iloc[0]['gain_loss'] < 0  # Should be a loss
            
        finally:
            os.unlink(input_file)
    
    @patch('calculate.fetch_price')
    def test_staking_income_calculation(self, mock_fetch_price):
        """Test staking income calculation with price fetching."""
        mock_fetch_price.return_value = 3000.0  # $3000 per ETH
        
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,stake,ETH,1.0,,0.0,0.0,,Staking reward"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            # Should have income from staking
            assert income > 0
            assert len(calculator.income_events) == 1
            
            # Income should be 1.0 ETH * $3000 = $3000
            assert abs(income - 3000.0) < 0.01
            
        finally:
            os.unlink(input_file)
    
    @patch('calculate.fetch_price')
    def test_airdrop_income_calculation(self, mock_fetch_price):
        """Test airdrop income calculation."""
        mock_fetch_price.return_value = 100.0  # $100 per token
        
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,airdrop,TOKEN,50.0,,0.0,0.0,,Airdrop received"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            # Should have income from airdrop: 50 * $100 = $5000
            assert abs(income - 5000.0) < 0.01
            
        finally:
            os.unlink(input_file)
    
    def test_complex_trading_scenario(self):
        """Test complex trading scenario with multiple buys and sells."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,2.0,USD,80000.0,40.0,USD,
2024-02-01T00:00:00,sell,BTC,0.5,USD,25000.0,12.5,USD,
2024-03-01T00:00:00,buy,BTC,1.0,USD,55000.0,27.5,USD,
2024-04-01T00:00:00,sell,BTC,1.5,USD,90000.0,45.0,USD,
2024-05-01T00:00:00,sell,BTC,1.0,USD,65000.0,32.5,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            # Should have 3 sale transactions
            assert len(gains_df) == 3
            
            # All should be short-term (less than 1 year)
            assert all(gains_df['short_term'])
            
            # Total amount sold should be 3.0 BTC
            total_sold = gains_df['amount'].sum()
            assert abs(total_sold - 3.0) < 0.001
            
        finally:
            os.unlink(input_file)
    
    def test_wash_sale_detection(self):
        """Test detection of potential wash sales."""
        # Buy, sell at loss, buy again within 30 days
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,1.0,USD,60000.0,30.0,USD,
2024-01-15T00:00:00,sell,BTC,1.0,USD,50000.0,25.0,USD,
2024-01-20T00:00:00,buy,BTC,1.0,USD,52000.0,26.0,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            # Should detect the loss
            assert len(gains_df) == 1
            assert gains_df.iloc[0]['gain_loss'] < 0  # Loss
            
            # Note: Actual wash sale handling would require more complex logic
            
        finally:
            os.unlink(input_file)
    
    def test_crypto_to_crypto_trades(self):
        """Test crypto-to-crypto trading scenarios."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,1.0,USD,50000.0,25.0,USD,
2024-02-01T00:00:00,buy,ETH,10.0,BTC,0.5,0.001,BTC,BTC to ETH trade"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            # The BTC-to-ETH trade should be treated as a sale of BTC
            # This would require price fetching for proper calculation
            # For now, just verify structure
            assert isinstance(gains_df, pd.DataFrame)
            
        finally:
            os.unlink(input_file)
    
    def test_fee_handling(self):
        """Test proper handling of transaction fees."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,1.0,USD,50000.0,100.0,USD,High fee
2024-06-01T00:00:00,sell,BTC,1.0,USD,55000.0,200.0,USD,High fee"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            # Fees should be included in cost basis and reduce proceeds
            # Cost basis: 50000 + 100 = 50100
            # Proceeds: 55000 - 200 = 54800
            # Gain: 54800 - 50100 = 4700
            expected_gain = 54800.0 - 50100.0
            assert abs(gains_df.iloc[0]['gain_loss'] - expected_gain) < 0.01
            
        finally:
            os.unlink(input_file)
    
    def test_empty_file_handling(self):
        """Test handling of empty transaction file."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            assert len(gains_df) == 0
            assert income == 0
            
        finally:
            os.unlink(input_file)
    
    def test_invalid_method(self):
        """Test invalid tax calculation method."""
        with pytest.raises((ValueError, TaxCalculationError)):
            TaxCalculator('invalid_method', 'usd')
    
    def test_invalid_currency(self):
        """Test invalid tax currency."""
        with pytest.raises((ValueError, TaxCalculationError)):
            TaxCalculator('fifo', 'invalid_currency')


if __name__ == '__main__':
    pytest.main([__file__])


class TestCalculateTaxesFunction:
    """Test cases for the main calculate_taxes function."""
    
    def test_calculate_taxes_function_basic(self):
        """Test the main calculate_taxes function."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,1.0,USD,50000.0,25.0,USD,
2024-06-01T00:00:00,sell,BTC,0.5,USD,30000.0,15.0,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            # Test function call
            result = calculate_taxes(input_file, method='fifo', tax_currency='usd')
            
            assert isinstance(result, dict)
            assert 'gains' in result
            assert 'income' in result
            assert 'summary' in result
            
            # Check summary statistics
            summary = result['summary']
            assert 'total_short_term_gains' in summary
            assert 'total_long_term_gains' in summary
            assert 'total_income' in summary
            
        finally:
            os.unlink(input_file)
    
    def test_calculate_taxes_with_output_file(self):
        """Test calculate_taxes with output file generation."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,1.0,USD,50000.0,25.0,USD,
2024-06-01T00:00:00,sell,BTC,0.5,USD,30000.0,15.0,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name
        
        try:
            result = calculate_taxes(input_file, method='fifo', tax_currency='usd', 
                                   output_file=output_file)
            
            # Check that output file was created
            assert os.path.exists(output_file)
            
            # Verify output file content
            output_df = pd.read_csv(output_file)
            assert len(output_df) > 0
            
        finally:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)


class TestTaxCalculationEdgeCases:
    """Test edge cases in tax calculations."""
    
    def test_zero_amount_transactions(self):
        """Test handling of zero-amount transactions."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,0.0,USD,0.0,0.0,USD,Zero amount
2024-01-02T00:00:00,buy,BTC,1.0,USD,50000.0,25.0,USD,Normal
2024-06-01T00:00:00,sell,BTC,0.5,USD,30000.0,15.0,USD,Normal"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            # Should handle zero amounts gracefully
            assert len(gains_df) == 1  # Only the real sale
            
        finally:
            os.unlink(input_file)
    
    def test_very_small_amounts(self):
        """Test handling of very small cryptocurrency amounts."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,0.00000001,USD,0.50,0.01,USD,1 satoshi
2024-06-01T00:00:00,sell,BTC,0.00000001,USD,0.60,0.01,USD,1 satoshi"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            # Should handle very small amounts without precision errors
            assert len(gains_df) == 1
            assert gains_df.iloc[0]['amount'] == 0.00000001
            
        finally:
            os.unlink(input_file)
    
    def test_very_large_amounts(self):
        """Test handling of very large amounts."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,SHIB,1000000000.0,USD,1000.0,5.0,USD,1B SHIB
2024-06-01T00:00:00,sell,SHIB,500000000.0,USD,600.0,3.0,USD,500M SHIB"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            # Should handle large amounts
            assert len(gains_df) == 1
            assert gains_df.iloc[0]['amount'] == 500000000.0
            
        finally:
            os.unlink(input_file)
    
    def test_same_day_buy_sell(self):
        """Test buy and sell on the same day."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T09:00:00,buy,BTC,1.0,USD,50000.0,25.0,USD,
2024-01-01T15:00:00,sell,BTC,1.0,USD,52000.0,26.0,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            # Should be short-term gain
            assert len(gains_df) == 1
            assert gains_df.iloc[0]['short_term'] == True
            
            # Gain should be: (52000 - 26) - (50000 + 25) = 1949
            expected_gain = 51974.0 - 50025.0
            assert abs(gains_df.iloc[0]['gain_loss'] - expected_gain) < 0.01
            
        finally:
            os.unlink(input_file)
    
    def test_leap_year_long_term_calculation(self):
        """Test long-term calculation across leap year."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2023-02-28T00:00:00,buy,BTC,1.0,USD,30000.0,15.0,USD,
2024-03-01T00:00:00,sell,BTC,1.0,USD,50000.0,25.0,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            # Should be long-term (more than 365 days, accounting for leap year)
            assert len(gains_df) == 1
            assert gains_df.iloc[0]['short_term'] == False
            
        finally:
            os.unlink(input_file)


class TestTaxCalculationPerformance:
    """Performance tests for tax calculations."""
    
    def test_large_dataset_performance(self):
        """Test performance with large number of transactions."""
        # Generate large dataset
        rows = []
        for i in range(1000):
            # Alternate between buys and sells
            if i % 2 == 0:
                rows.append(f"2024-01-{(i % 30) + 1:02d}T{(i % 24):02d}:00:00,buy,BTC,{0.001 * (i + 1):.6f},USD,{50000 + i * 10:.2f},{25 + i * 0.1:.2f},USD,")
            else:
                rows.append(f"2024-01-{(i % 30) + 1:02d}T{(i % 24):02d}:00:00,sell,BTC,{0.0005 * i:.6f},USD,{51000 + i * 5:.2f},{26 + i * 0.05:.2f},USD,")
        
        test_data = "timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes\n" + "\n".join(rows)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            import time
            start_time = time.time()
            
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Should complete within reasonable time
            assert processing_time < 30  # Adjust threshold as needed
            
            # Should process all transactions
            assert isinstance(gains_df, pd.DataFrame)
            
        finally:
            os.unlink(input_file)
    
    def test_memory_usage_large_dataset(self):
        """Test memory usage with large datasets."""
        # This would require memory profiling tools in production
        # For now, just ensure it doesn't crash
        
        rows = []
        for i in range(2000):
            rows.append(f"2024-01-01T00:00:00,buy,BTC,1.0,USD,50000.0,25.0,USD,")
        
        test_data = "timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes\n" + "\n".join(rows)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            gains_df, income = calculator.calculate_taxes(input_file)
            
            # Should not crash with memory errors
            assert isinstance(gains_df, pd.DataFrame)
            
        finally:
            os.unlink(input_file)


class TestTaxCalculationErrorHandling:
    """Test error handling in tax calculations."""
    
    def test_invalid_file_format(self):
        """Test handling of invalid file format."""
        test_data = """invalid,csv,format
not,a,transaction,file"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            
            with pytest.raises((ValueError, TaxCalculationError, KeyError)):
                calculator.calculate_taxes(input_file)
                
        finally:
            os.unlink(input_file)
    
    def test_missing_required_columns(self):
        """Test handling of missing required columns."""
        test_data = """timestamp,type,base_asset
2024-01-01T00:00:00,buy,BTC"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            
            with pytest.raises((ValueError, TaxCalculationError, KeyError)):
                calculator.calculate_taxes(input_file)
                
        finally:
            os.unlink(input_file)
    
    def test_corrupted_data_handling(self):
        """Test handling of corrupted transaction data."""
        test_data = """timestamp,type,base_asset,base_amount,quote_asset,quote_amount,fee_amount,fee_asset,notes
2024-01-01T00:00:00,buy,BTC,not_a_number,USD,50000.0,25.0,USD,
invalid_date,sell,BTC,0.5,USD,30000.0,15.0,USD,"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_data)
            input_file = f.name
        
        try:
            calculator = TaxCalculator('fifo', 'usd')
            
            # Should either handle gracefully or raise appropriate error
            try:
                gains_df, income = calculator.calculate_taxes(input_file)
                # If it succeeds, verify it handled the bad data
                assert isinstance(gains_df, pd.DataFrame)
            except (ValueError, TaxCalculationError):
                # Expected behavior for corrupted data
                pass
                
        finally:
            os.unlink(input_file)
    
    def test_nonexistent_file(self):
        """Test handling of non-existent input file."""
        calculator = TaxCalculator('fifo', 'usd')
        
        with pytest.raises((FileNotFoundError, TaxCalculationError)):
            calculator.calculate_taxes('nonexistent_file.csv')


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])