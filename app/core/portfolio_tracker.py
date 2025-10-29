"""
Portfolio tracking and analytics module for cryptocurrency portfolios.
Provides portfolio performance analysis, asset allocation, and risk metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import json
import os

logger = logging.getLogger(__name__)

class PortfolioTracker:
    """Track and analyze cryptocurrency portfolio performance."""
    
    def __init__(self):
        self.holdings = {}  # asset -> amount
        self.transactions = pd.DataFrame()
        self.price_history = {}  # asset -> price data
        self.portfolio_value_history = []
        
    def load_transactions(self, transactions_df: pd.DataFrame) -> None:
        """Load transaction data for portfolio tracking."""
        self.transactions = transactions_df.copy()
        self.transactions['timestamp'] = pd.to_datetime(self.transactions['timestamp'])
        self.transactions = self.transactions.sort_values('timestamp')
        
        # Calculate current holdings
        self._calculate_holdings()
        
    def _calculate_holdings(self) -> None:
        """Calculate current holdings from transaction history."""
        self.holdings = {}
        
        for _, tx in self.transactions.iterrows():
            asset = tx['base_asset']
            amount = tx['base_amount']
            tx_type = tx['type'].lower()
            
            if asset not in self.holdings:
                self.holdings[asset] = 0.0
            
            if tx_type in ['buy', 'receive', 'deposit', 'stake', 'airdrop']:
                self.holdings[asset] += amount
            elif tx_type in ['sell', 'send', 'withdraw']:
                self.holdings[asset] -= amount
            elif tx_type == 'trade':
                # For trades, we need to handle both sides
                if tx['base_asset'] == asset:
                    self.holdings[asset] -= amount
                if tx['quote_asset'] == asset:
                    self.holdings[asset] += tx['quote_amount']
    
    def get_portfolio_summary(self, current_prices: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Get portfolio summary with current values.
        
        Args:
            current_prices: Current prices for assets (optional)
            
        Returns:
            Dictionary with portfolio summary
        """
        if not current_prices:
            current_prices = self._get_current_prices()
        
        total_value = 0.0
        asset_values = {}
        
        for asset, amount in self.holdings.items():
            if amount > 0 and asset in current_prices:
                value = amount * current_prices[asset]
                asset_values[asset] = {
                    'amount': amount,
                    'price': current_prices[asset],
                    'value': value,
                    'percentage': 0.0  # Will be calculated after total
                }
                total_value += value
        
        # Calculate percentages
        for asset in asset_values:
            if total_value > 0:
                asset_values[asset]['percentage'] = (asset_values[asset]['value'] / total_value) * 100
        
        return {
            'total_value': total_value,
            'total_assets': len([a for a in self.holdings.values() if a > 0]),
            'asset_values': asset_values,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_performance_metrics(self, start_date: Optional[datetime] = None, 
                               end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Calculate portfolio performance metrics.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary with performance metrics
        """
        if self.transactions.empty:
            return {}
        
        # Filter transactions by date range
        filtered_txs = self.transactions.copy()
        if start_date:
            filtered_txs = filtered_txs[filtered_txs['timestamp'] >= start_date]
        if end_date:
            filtered_txs = filtered_txs[filtered_txs['timestamp'] <= end_date]
        
        if filtered_txs.empty:
            return {}
        
        # Calculate metrics
        total_trades = len(filtered_txs)
        total_volume = filtered_txs['quote_amount'].sum()
        
        # Calculate P&L
        buy_txs = filtered_txs[filtered_txs['type'].isin(['buy', 'receive', 'deposit'])]
        sell_txs = filtered_txs[filtered_txs['type'].isin(['sell', 'send', 'withdraw'])]
        
        total_bought = buy_txs['quote_amount'].sum()
        total_sold = sell_txs['quote_amount'].sum()
        realized_pnl = total_sold - total_bought
        
        # Calculate unrealized P&L (current holdings value)
        current_prices = self._get_current_prices()
        current_value = 0.0
        cost_basis = 0.0
        
        for asset, amount in self.holdings.items():
            if amount > 0 and asset in current_prices:
                current_value += amount * current_prices[asset]
                # Estimate cost basis (simplified)
                asset_txs = filtered_txs[filtered_txs['base_asset'] == asset]
                if not asset_txs.empty:
                    avg_price = asset_txs['quote_amount'].sum() / asset_txs['base_amount'].sum()
                    cost_basis += amount * avg_price
        
        unrealized_pnl = current_value - cost_basis
        
        # Calculate win rate
        profitable_trades = 0
        total_trade_pairs = 0
        
        for asset in self.holdings:
            asset_txs = filtered_txs[filtered_txs['base_asset'] == asset]
            if len(asset_txs) > 1:
                # Simple win rate calculation
                buy_price = asset_txs[asset_txs['type'] == 'buy']['quote_amount'].mean()
                sell_price = asset_txs[asset_txs['type'] == 'sell']['quote_amount'].mean()
                if not pd.isna(buy_price) and not pd.isna(sell_price):
                    total_trade_pairs += 1
                    if sell_price > buy_price:
                        profitable_trades += 1
        
        win_rate = (profitable_trades / total_trade_pairs * 100) if total_trade_pairs > 0 else 0
        
        return {
            'total_trades': total_trades,
            'total_volume': total_volume,
            'realized_pnl': realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'total_pnl': realized_pnl + unrealized_pnl,
            'current_value': current_value,
            'cost_basis': cost_basis,
            'win_rate': win_rate,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None
        }
    
    def get_asset_allocation(self) -> Dict[str, Any]:
        """Get asset allocation breakdown."""
        summary = self.get_portfolio_summary()
        
        if not summary['asset_values']:
            return {}
        
        # Sort by value
        sorted_assets = sorted(
            summary['asset_values'].items(),
            key=lambda x: x[1]['value'],
            reverse=True
        )
        
        allocation = {
            'total_value': summary['total_value'],
            'assets': []
        }
        
        for asset, data in sorted_assets:
            allocation['assets'].append({
                'asset': asset,
                'amount': data['amount'],
                'value': data['value'],
                'percentage': data['percentage'],
                'price': data['price']
            })
        
        return allocation
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """Calculate portfolio risk metrics."""
        if len(self.holdings) < 2:
            return {'error': 'Need at least 2 assets for risk analysis'}
        
        # Get asset values
        summary = self.get_portfolio_summary()
        asset_values = summary['asset_values']
        
        if len(asset_values) < 2:
            return {'error': 'Need at least 2 assets for risk analysis'}
        
        # Calculate concentration risk
        values = [data['value'] for data in asset_values.values()]
        total_value = sum(values)
        
        # Herfindahl-Hirschman Index (concentration measure)
        hhi = sum((value / total_value) ** 2 for value in values)
        
        # Largest holding percentage
        max_holding = max(values) / total_value * 100
        
        # Number of significant holdings (>5% of portfolio)
        significant_holdings = sum(1 for value in values if value / total_value > 0.05)
        
        return {
            'concentration_index': hhi,
            'max_holding_percentage': max_holding,
            'significant_holdings_count': significant_holdings,
            'diversification_score': 1 - hhi,  # Higher is better
            'risk_level': self._assess_risk_level(hhi, max_holding)
        }
    
    def _assess_risk_level(self, hhi: float, max_holding: float) -> str:
        """Assess portfolio risk level based on concentration metrics."""
        if hhi > 0.5 or max_holding > 50:
            return 'High'
        elif hhi > 0.25 or max_holding > 25:
            return 'Medium'
        else:
            return 'Low'
    
    def get_trading_activity(self, days: int = 30) -> Dict[str, Any]:
        """Get trading activity summary for the last N days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        recent_txs = self.transactions[
            (self.transactions['timestamp'] >= start_date) &
            (self.transactions['timestamp'] <= end_date)
        ]
        
        if recent_txs.empty:
            return {
                'days_analyzed': days,
                'total_trades': 0,
                'trades_per_day': 0,
                'most_traded_asset': None,
                'trading_volume': 0
            }
        
        # Calculate metrics
        total_trades = len(recent_txs)
        trades_per_day = total_trades / days
        
        # Most traded asset
        asset_counts = recent_txs['base_asset'].value_counts()
        most_traded = asset_counts.index[0] if not asset_counts.empty else None
        
        # Trading volume
        trading_volume = recent_txs['quote_amount'].sum()
        
        return {
            'days_analyzed': days,
            'total_trades': total_trades,
            'trades_per_day': round(trades_per_day, 2),
            'most_traded_asset': most_traded,
            'trading_volume': trading_volume,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
    
    def generate_portfolio_report(self, output_file: str = 'output/portfolio_report.json') -> Dict[str, Any]:
        """Generate comprehensive portfolio report."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_portfolio_summary(),
            'performance': self.get_performance_metrics(),
            'allocation': self.get_asset_allocation(),
            'risk_metrics': self.get_risk_metrics(),
            'trading_activity_30d': self.get_trading_activity(30),
            'trading_activity_7d': self.get_trading_activity(7)
        }
        
        # Save report
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Portfolio report saved to {output_file}")
        return report
    
    def _get_current_prices(self) -> Dict[str, float]:
        """Get current prices for all assets in portfolio."""
        # This would typically fetch from an API
        # For now, return mock prices
        mock_prices = {
            'BTC': 45000.0,
            'ETH': 3000.0,
            'BNB': 300.0,
            'ADA': 0.5,
            'DOT': 20.0,
            'LINK': 15.0,
            'UNI': 25.0,
            'AAVE': 100.0,
            'MATIC': 1.0,
            'SOL': 100.0
        }
        
        # Return prices for assets in portfolio
        return {asset: mock_prices.get(asset, 1.0) for asset in self.holdings.keys()}


def analyze_portfolio(transactions_file: str, output_file: str = 'output/portfolio_analysis.json') -> Dict[str, Any]:
    """
    Convenience function to analyze portfolio from transaction file.
    
    Args:
        transactions_file: Path to normalized transaction CSV file
        output_file: Output file for portfolio analysis
        
    Returns:
        Dictionary with portfolio analysis
    """
    # Load transactions
    df = pd.read_csv(transactions_file)
    
    # Create tracker and analyze
    tracker = PortfolioTracker()
    tracker.load_transactions(df)
    
    # Generate report
    return tracker.generate_portfolio_report(output_file)
