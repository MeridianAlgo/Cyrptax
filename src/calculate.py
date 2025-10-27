"""Tax calculation engine for computing capital gains, losses, and income."""

import pandas as pd
from collections import deque
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
import os

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from price_fetch import fetch_price
from config import config

logger = logging.getLogger(__name__)


class TaxLot:
    """Represents a tax lot (inventory position) for an asset."""
    
    def __init__(self, amount: float, cost_basis: float, acquisition_date: datetime, 
                 transaction_id: Optional[str] = None):
        self.amount = amount
        self.cost_basis = cost_basis  # Total cost for this lot
        self.acquisition_date = acquisition_date
        self.transaction_id = transaction_id
        self.unit_cost = cost_basis / amount if amount > 0 else 0
    
    def __repr__(self):
        return f"TaxLot(amount={self.amount}, cost_basis={self.cost_basis}, date={self.acquisition_date})"


class AssetInventory:
    """Manages inventory for a single asset using different accounting methods."""
    
    def __init__(self, asset: str, method: str = 'fifo'):
        self.asset = asset
        self.method = method.lower()
        self.lots = deque() if method.lower() == 'fifo' else []
        self.total_amount = 0.0
        self.total_cost_basis = 0.0
    
    def add_lot(self, lot: TaxLot) -> None:
        """Add a new tax lot to inventory."""
        if self.method == 'fifo':
            self.lots.append(lot)
        elif self.method == 'lifo':
            self.lots.append(lot)
        elif self.method == 'hifo':
            self.lots.append(lot)
            # Sort by unit cost (highest first)
            self.lots.sort(key=lambda x: x.unit_cost, reverse=True)
        
        self.total_amount += lot.amount
        self.total_cost_basis += lot.cost_basis
        
        logger.debug(f"Added lot to {self.asset}: {lot}")
    
    def remove_amount(self, amount: float) -> List[Tuple[TaxLot, float]]:
        """
        Remove amount from inventory and return list of (lot, amount_taken) tuples.
        
        Args:
            amount: Amount to remove from inventory
            
        Returns:
            List of (TaxLot, amount_taken) tuples representing what was sold
        """
        if amount <= 0:
            return []
        
        if self.total_amount < amount - 1e-8:  # Small tolerance for floating point
            logger.warning(f"Insufficient {self.asset} inventory: need {amount}, have {self.total_amount}")
        
        removed_lots = []
        remaining_to_remove = amount
        
        while remaining_to_remove > 1e-8 and self.lots:
            if self.method == 'fifo':
                lot = self.lots.popleft()
            elif self.method == 'lifo':
                lot = self.lots.pop()
            elif self.method == 'hifo':
                lot = self.lots.pop(0)  # Already sorted by highest cost
            
            if lot.amount <= remaining_to_remove:
                # Take entire lot
                removed_lots.append((lot, lot.amount))
                remaining_to_remove -= lot.amount
                self.total_amount -= lot.amount
                self.total_cost_basis -= lot.cost_basis
            else:
                # Take partial lot
                taken_amount = remaining_to_remove
                taken_cost = (lot.cost_basis / lot.amount) * taken_amount
                
                # Create lot for taken portion
                taken_lot = TaxLot(taken_amount, taken_cost, lot.acquisition_date, lot.transaction_id)
                removed_lots.append((taken_lot, taken_amount))
                
                # Update remaining lot
                lot.amount -= taken_amount
                lot.cost_basis -= taken_cost
                
                # Put remaining lot back
                if self.method == 'fifo':
                    self.lots.appendleft(lot)
                elif self.method == 'lifo':
                    self.lots.append(lot)
                elif self.method == 'hifo':
                    self.lots.insert(0, lot)
                
                self.total_amount -= taken_amount
                self.total_cost_basis -= taken_cost
                remaining_to_remove = 0
        
        return removed_lots


class TaxCalculator:
    """Main tax calculation engine."""
    
    def __init__(self, method: str = 'fifo', tax_currency: str = 'usd'):
        self.method = method.lower()
        self.tax_currency = tax_currency.lower()
        self.inventories: Dict[str, AssetInventory] = {}
        self.gains_losses: List[Dict[str, Any]] = []
        self.income_events: List[Dict[str, Any]] = []
        self.total_short_term_gains = 0.0
        self.total_long_term_gains = 0.0
        self.total_income = 0.0
    
    def calculate_taxes(self, input_file: str) -> Tuple[pd.DataFrame, float]:
        """
        Calculate taxes from normalized transaction data.
        
        Args:
            input_file: Path to normalized CSV file
            
        Returns:
            Tuple of (gains_losses_df, total_income)
        """
        # Load and validate data with memory optimization
        try:
            # Check file size and use appropriate loading strategy
            file_size = os.path.getsize(input_file)
            if file_size > 100 * 1024 * 1024:  # 100MB
                logger.info(f"Large file detected ({file_size / 1024 / 1024:.1f}MB), using optimized loading")
                df = pd.read_csv(input_file, dtype={'base_amount': 'float32', 'quote_amount': 'float32', 'fee_amount': 'float32'})
            else:
                df = pd.read_csv(input_file)
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            logger.info(f"Processing {len(df)} transactions for tax calculations")
            
        except Exception as e:
            logger.error(f"Error loading transaction data: {e}")
            raise CalculationError(f"Failed to load transaction data: {e}")
        
        # Process each transaction
        for idx, row in df.iterrows():
            try:
                self._process_transaction(row, idx)
            except Exception as e:
                logger.error(f"Error processing transaction {idx}: {e}")
                continue
        
        # Create results DataFrame
        gains_df = pd.DataFrame(self.gains_losses)
        
        # Calculate totals
        if not gains_df.empty:
            self.total_short_term_gains = gains_df[gains_df['short_term']]['gain_loss'].sum()
            self.total_long_term_gains = gains_df[~gains_df['short_term']]['gain_loss'].sum()
        
        self.total_income = sum(event['income_amount'] for event in self.income_events)
        
        # Log results
        logger.info(f"Tax calculation complete:")
        logger.info(f"  Short-term gains: {self.total_short_term_gains:.2f} {self.tax_currency.upper()}")
        logger.info(f"  Long-term gains: {self.total_long_term_gains:.2f} {self.tax_currency.upper()}")
        logger.info(f"  Total income: {self.total_income:.2f} {self.tax_currency.upper()}")
        
        # Save detailed results
        self._save_results(gains_df)
        
        return gains_df, self.total_income
    
    def _process_transaction(self, row: pd.Series, transaction_id: int) -> None:
        """Process a single transaction."""
        asset = row['base_asset']
        transaction_type = str(row['type']).lower()
        amount = float(row['base_amount']) if pd.notna(row['base_amount']) else 0
        timestamp = row['timestamp']
        
        if pd.isna(asset) or amount == 0:
            return
        
        # Ensure inventory exists for asset
        if asset not in self.inventories:
            self.inventories[asset] = AssetInventory(asset, self.method)
        
        inventory = self.inventories[asset]
        
        # Process based on transaction type
        if transaction_type in ['buy', 'deposit']:
            self._process_acquisition(row, inventory, transaction_id)
        elif transaction_type == 'sell':
            self._process_disposal(row, inventory, transaction_id)
        elif transaction_type in ['stake', 'airdrop']:
            self._process_income(row, inventory, transaction_id)
        elif transaction_type in ['withdraw', 'transfer_out']:
            self._process_withdrawal(row, inventory, transaction_id)
        elif transaction_type == 'fee':
            self._process_fee(row, inventory, transaction_id)
        else:
            logger.warning(f"Unknown transaction type: {transaction_type}")
    
    def _process_acquisition(self, row: pd.Series, inventory: AssetInventory, transaction_id: int) -> None:
        """Process buy/deposit transactions."""
        amount = float(row['base_amount'])
        quote_amount = float(row['quote_amount']) if pd.notna(row['quote_amount']) else 0
        fee_amount = float(row['fee_amount']) if pd.notna(row['fee_amount']) else 0
        
        # Calculate cost basis
        if quote_amount > 0:
            cost_basis = quote_amount + fee_amount
        else:
            # Fetch price if not available
            price = fetch_price(row['base_asset'], row['timestamp'], self.tax_currency)
            if price:
                cost_basis = (price * amount) + fee_amount
            else:
                logger.warning(f"No price available for {row['base_asset']} at {row['timestamp']}")
                cost_basis = fee_amount  # Just use fee as cost basis
        
        # Create and add tax lot
        lot = TaxLot(amount, cost_basis, row['timestamp'], str(transaction_id))
        inventory.add_lot(lot)
        
        logger.debug(f"Acquired {amount} {row['base_asset']} with cost basis {cost_basis}")
    
    def _process_disposal(self, row: pd.Series, inventory: AssetInventory, transaction_id: int) -> None:
        """Process sell transactions."""
        amount = float(row['base_amount'])
        quote_amount = float(row['quote_amount']) if pd.notna(row['quote_amount']) else 0
        fee_amount = float(row['fee_amount']) if pd.notna(row['fee_amount']) else 0
        
        # Calculate proceeds
        if quote_amount > 0:
            proceeds = quote_amount - fee_amount
        else:
            # Fetch price if not available
            price = fetch_price(row['base_asset'], row['timestamp'], self.tax_currency)
            if price:
                proceeds = (price * amount) - fee_amount
            else:
                logger.warning(f"No price available for sale of {row['base_asset']}")
                return
        
        # Remove from inventory and calculate gains/losses
        removed_lots = inventory.remove_amount(amount)
        
        for lot, lot_amount in removed_lots:
            # Calculate gain/loss for this lot
            lot_proceeds = (proceeds / amount) * lot_amount
            lot_cost_basis = (lot.cost_basis / lot.amount) * lot_amount
            gain_loss = lot_proceeds - lot_cost_basis
            
            # Determine if short-term or long-term
            holding_period = row['timestamp'] - lot.acquisition_date
            is_short_term = holding_period < timedelta(days=365)
            
            # Record gain/loss
            gain_record = {
                'date': row['timestamp'],
                'asset': row['base_asset'],
                'amount': lot_amount,
                'proceeds': lot_proceeds,
                'cost_basis': lot_cost_basis,
                'gain_loss': gain_loss,
                'short_term': is_short_term,
                'holding_period_days': holding_period.days,
                'acquisition_date': lot.acquisition_date,
                'method': self.method,
                'transaction_id': transaction_id
            }
            
            self.gains_losses.append(gain_record)
            
            logger.debug(f"Sold {lot_amount} {row['base_asset']}: "
                        f"proceeds={lot_proceeds:.2f}, cost={lot_cost_basis:.2f}, "
                        f"gain={gain_loss:.2f} ({'ST' if is_short_term else 'LT'})")
    
    def _process_income(self, row: pd.Series, inventory: AssetInventory, transaction_id: int) -> None:
        """Process staking/airdrop income transactions."""
        amount = float(row['base_amount'])
        
        # Get fair market value at time of receipt
        price = fetch_price(row['base_asset'], row['timestamp'], self.tax_currency)
        if not price:
            logger.warning(f"No price available for income event: {row['base_asset']}")
            return
        
        income_value = price * amount
        
        # Record income event
        income_record = {
            'date': row['timestamp'],
            'asset': row['base_asset'],
            'amount': amount,
            'price': price,
            'income_amount': income_value,
            'type': row['type'],
            'transaction_id': transaction_id
        }
        
        self.income_events.append(income_record)
        
        # Add to inventory with income value as cost basis
        lot = TaxLot(amount, income_value, row['timestamp'], str(transaction_id))
        inventory.add_lot(lot)
        
        logger.debug(f"Income: {amount} {row['base_asset']} worth {income_value:.2f}")
    
    def _process_withdrawal(self, row: pd.Series, inventory: AssetInventory, transaction_id: int) -> None:
        """Process withdrawal transactions (non-taxable disposal)."""
        amount = float(row['base_amount'])
        
        # Remove from inventory but don't record as taxable event
        removed_lots = inventory.remove_amount(amount)
        
        logger.debug(f"Withdrew {amount} {row['base_asset']} (non-taxable)")
    
    def _process_fee(self, row: pd.Series, inventory: AssetInventory, transaction_id: int) -> None:
        """Process fee transactions."""
        amount = float(row['base_amount'])
        
        # Treat fees as disposals for tax purposes
        price = fetch_price(row['base_asset'], row['timestamp'], self.tax_currency)
        if not price:
            logger.warning(f"No price available for fee: {row['base_asset']}")
            return
        
        proceeds = 0  # Fees have no proceeds
        
        # Remove from inventory and calculate loss
        removed_lots = inventory.remove_amount(amount)
        
        for lot, lot_amount in removed_lots:
            lot_cost_basis = (lot.cost_basis / lot.amount) * lot_amount
            gain_loss = proceeds - lot_cost_basis  # Will be negative (loss)
            
            holding_period = row['timestamp'] - lot.acquisition_date
            is_short_term = holding_period < timedelta(days=365)
            
            gain_record = {
                'date': row['timestamp'],
                'asset': row['base_asset'],
                'amount': lot_amount,
                'proceeds': proceeds,
                'cost_basis': lot_cost_basis,
                'gain_loss': gain_loss,
                'short_term': is_short_term,
                'holding_period_days': holding_period.days,
                'acquisition_date': lot.acquisition_date,
                'method': self.method,
                'transaction_id': transaction_id,
                'note': 'Fee transaction'
            }
            
            self.gains_losses.append(gain_record)
    
    def _save_results(self, gains_df: pd.DataFrame) -> None:
        """Save calculation results to files."""
        output_dir = config.get('output', 'reports_dir', 'output/reports')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save gains/losses
        if not gains_df.empty:
            gains_file = os.path.join(output_dir, 'gains_losses.csv')
            gains_df.to_csv(gains_file, index=False)
            logger.info(f"Gains/losses saved to {gains_file}")
        
        # Save income events
        if self.income_events:
            income_df = pd.DataFrame(self.income_events)
            income_file = os.path.join(output_dir, 'income_events.csv')
            income_df.to_csv(income_file, index=False)
            logger.info(f"Income events saved to {income_file}")
        
        # Save summary
        summary = {
            'method': self.method,
            'tax_currency': self.tax_currency,
            'total_short_term_gains': self.total_short_term_gains,
            'total_long_term_gains': self.total_long_term_gains,
            'total_income': self.total_income,
            'total_transactions': len(self.gains_losses) + len(self.income_events)
        }
        
        summary_file = os.path.join(output_dir, 'tax_summary.json')
        import json
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Tax summary saved to {summary_file}")


def calculate_taxes(input_file: str, method: str = 'fifo', tax_currency: str = 'usd') -> Tuple[pd.DataFrame, float]:
    """
    Convenience function to calculate taxes.
    
    Args:
        input_file: Path to normalized CSV file
        method: Tax accounting method ('fifo', 'lifo', 'hifo')
        tax_currency: Currency for tax calculations
        
    Returns:
        Tuple of (gains_losses_df, total_income)
    """
    calculator = TaxCalculator(method, tax_currency)
    return calculator.calculate_taxes(input_file)