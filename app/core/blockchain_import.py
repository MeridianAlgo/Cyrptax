"""
Blockchain data import module for direct blockchain transaction fetching.
Supports Ethereum, Bitcoin, and other major blockchains.
"""

import requests
import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import time
import json

logger = logging.getLogger(__name__)

class BlockchainImporter:
    """Import transaction data directly from blockchain APIs."""
    
    def __init__(self):
        self.etherscan_api_key = None  # Set via environment variable
        self.bitcoin_api_key = None    # Set via environment variable
        self.rate_limit_delay = 0.2    # Delay between API calls
        
    def import_ethereum_transactions(self, address: str, start_date: Optional[datetime] = None, 
                                   end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Import Ethereum transactions from Etherscan API.
        
        Args:
            address: Ethereum wallet address
            start_date: Start date for transactions (optional)
            end_date: End date for transactions (optional)
            
        Returns:
            DataFrame with normalized transaction data
        """
        if not self.etherscan_api_key:
            logger.warning("Etherscan API key not set. Set ETHERSCAN_API_KEY environment variable.")
            return pd.DataFrame()
        
        transactions = []
        page = 1
        
        while True:
            try:
                # Get normal transactions
                normal_txs = self._get_ethereum_transactions(address, 'normal', page)
                if not normal_txs:
                    break
                
                # Get internal transactions
                internal_txs = self._get_ethereum_transactions(address, 'internal', page)
                
                # Process transactions
                for tx in normal_txs + internal_txs:
                    processed_tx = self._process_ethereum_transaction(tx, address)
                    if processed_tx and self._is_in_date_range(processed_tx['timestamp'], start_date, end_date):
                        transactions.append(processed_tx)
                
                page += 1
                time.sleep(self.rate_limit_delay)
                
                # Limit to prevent excessive API calls
                if page > 100:
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching Ethereum transactions: {e}")
                break
        
        return pd.DataFrame(transactions)
    
    def import_bitcoin_transactions(self, address: str, start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Import Bitcoin transactions from blockchain.info API.
        
        Args:
            address: Bitcoin wallet address
            start_date: Start date for transactions (optional)
            end_date: End date for transactions (optional)
            
        Returns:
            DataFrame with normalized transaction data
        """
        transactions = []
        
        try:
            # Get address info
            url = f"https://blockchain.info/rawaddr/{address}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for tx in data.get('txs', []):
                processed_tx = self._process_bitcoin_transaction(tx, address)
                if processed_tx and self._is_in_date_range(processed_tx['timestamp'], start_date, end_date):
                    transactions.append(processed_tx)
                
                time.sleep(self.rate_limit_delay)
                
        except Exception as e:
            logger.error(f"Error fetching Bitcoin transactions: {e}")
        
        return pd.DataFrame(transactions)
    
    def import_bsc_transactions(self, address: str, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Import BSC (Binance Smart Chain) transactions from BSCScan API.
        
        Args:
            address: BSC wallet address
            start_date: Start date for transactions (optional)
            end_date: End date for transactions (optional)
            
        Returns:
            DataFrame with normalized transaction data
        """
        if not self.etherscan_api_key:
            logger.warning("BSCScan API key not set. Set ETHERSCAN_API_KEY environment variable.")
            return pd.DataFrame()
        
        transactions = []
        page = 1
        
        while True:
            try:
                # BSCScan uses similar API to Etherscan
                url = "https://api.bscscan.com/api"
                params = {
                    'module': 'account',
                    'action': 'txlist',
                    'address': address,
                    'startblock': 0,
                    'endblock': 99999999,
                    'page': page,
                    'offset': 10000,
                    'sort': 'asc',
                    'apikey': self.etherscan_api_key
                }
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                if data['status'] != '1' or not data['result']:
                    break
                
                for tx in data['result']:
                    processed_tx = self._process_bsc_transaction(tx, address)
                    if processed_tx and self._is_in_date_range(processed_tx['timestamp'], start_date, end_date):
                        transactions.append(processed_tx)
                
                page += 1
                time.sleep(self.rate_limit_delay)
                
                if page > 100:  # Limit pages
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching BSC transactions: {e}")
                break
        
        return pd.DataFrame(transactions)
    
    def import_polygon_transactions(self, address: str, start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Import Polygon transactions from PolygonScan API.
        
        Args:
            address: Polygon wallet address
            start_date: Start date for transactions (optional)
            end_date: End date for transactions (optional)
            
        Returns:
            DataFrame with normalized transaction data
        """
        if not self.etherscan_api_key:
            logger.warning("PolygonScan API key not set. Set ETHERSCAN_API_KEY environment variable.")
            return pd.DataFrame()
        
        transactions = []
        page = 1
        
        while True:
            try:
                url = "https://api.polygonscan.com/api"
                params = {
                    'module': 'account',
                    'action': 'txlist',
                    'address': address,
                    'startblock': 0,
                    'endblock': 99999999,
                    'page': page,
                    'offset': 10000,
                    'sort': 'asc',
                    'apikey': self.etherscan_api_key
                }
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                if data['status'] != '1' or not data['result']:
                    break
                
                for tx in data['result']:
                    processed_tx = self._process_polygon_transaction(tx, address)
                    if processed_tx and self._is_in_date_range(processed_tx['timestamp'], start_date, end_date):
                        transactions.append(processed_tx)
                
                page += 1
                time.sleep(self.rate_limit_delay)
                
                if page > 100:
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching Polygon transactions: {e}")
                break
        
        return pd.DataFrame(transactions)
    
    def _get_ethereum_transactions(self, address: str, tx_type: str, page: int) -> List[Dict]:
        """Get Ethereum transactions from Etherscan API."""
        url = "https://api.etherscan.io/api"
        params = {
            'module': 'account',
            'action': 'txlist' if tx_type == 'normal' else 'txlistinternal',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'page': page,
            'offset': 10000,
            'sort': 'asc',
            'apikey': self.etherscan_api_key
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if data['status'] != '1':
            return []
        
        return data['result']
    
    def _process_ethereum_transaction(self, tx: Dict, address: str) -> Optional[Dict]:
        """Process Ethereum transaction into standard format."""
        try:
            timestamp = datetime.fromtimestamp(int(tx['timeStamp']))
            
            # Determine transaction type and amounts
            if tx['from'].lower() == address.lower():
                # Outgoing transaction
                tx_type = 'sell' if tx['value'] != '0' else 'transfer'
                base_amount = float(tx['value']) / 1e18  # Convert from wei
                quote_amount = float(tx.get('gasUsed', 0)) * float(tx.get('gasPrice', 0)) / 1e18
                base_asset = 'ETH'
                quote_asset = 'ETH'
            else:
                # Incoming transaction
                tx_type = 'buy' if tx['value'] != '0' else 'receive'
                base_amount = float(tx['value']) / 1e18
                quote_amount = 0
                base_asset = 'ETH'
                quote_asset = 'ETH'
            
            return {
                'timestamp': timestamp.isoformat(),
                'type': tx_type,
                'base_asset': base_asset,
                'base_amount': base_amount,
                'quote_asset': quote_asset,
                'quote_amount': quote_amount,
                'fee_amount': float(tx.get('gasUsed', 0)) * float(tx.get('gasPrice', 0)) / 1e18,
                'fee_asset': 'ETH',
                'notes': f"Ethereum tx: {tx['hash']}"
            }
        except Exception as e:
            logger.error(f"Error processing Ethereum transaction: {e}")
            return None
    
    def _process_bitcoin_transaction(self, tx: Dict, address: str) -> Optional[Dict]:
        """Process Bitcoin transaction into standard format."""
        try:
            timestamp = datetime.fromtimestamp(tx['time'])
            
            # Calculate input and output amounts for this address
            input_amount = 0
            output_amount = 0
            
            for inp in tx.get('inputs', []):
                if inp.get('prev_out', {}).get('addr') == address:
                    input_amount += inp['prev_out']['value']
            
            for out in tx.get('out', []):
                if out.get('addr') == address:
                    output_amount += out['value']
            
            # Determine transaction type
            if input_amount > 0 and output_amount > 0:
                tx_type = 'trade'
            elif input_amount > 0:
                tx_type = 'sell'
            else:
                tx_type = 'buy'
            
            amount = max(input_amount, output_amount) / 1e8  # Convert from satoshis
            
            return {
                'timestamp': timestamp.isoformat(),
                'type': tx_type,
                'base_asset': 'BTC',
                'base_amount': amount,
                'quote_asset': 'BTC',
                'quote_amount': amount,
                'fee_amount': 0,  # Bitcoin fees are implicit
                'fee_asset': 'BTC',
                'notes': f"Bitcoin tx: {tx['hash']}"
            }
        except Exception as e:
            logger.error(f"Error processing Bitcoin transaction: {e}")
            return None
    
    def _process_bsc_transaction(self, tx: Dict, address: str) -> Optional[Dict]:
        """Process BSC transaction into standard format."""
        try:
            timestamp = datetime.fromtimestamp(int(tx['timeStamp']))
            
            if tx['from'].lower() == address.lower():
                tx_type = 'sell'
                base_amount = float(tx['value']) / 1e18
                quote_amount = float(tx.get('gasUsed', 0)) * float(tx.get('gasPrice', 0)) / 1e18
            else:
                tx_type = 'buy'
                base_amount = float(tx['value']) / 1e18
                quote_amount = 0
            
            return {
                'timestamp': timestamp.isoformat(),
                'type': tx_type,
                'base_asset': 'BNB',
                'base_amount': base_amount,
                'quote_asset': 'BNB',
                'quote_amount': quote_amount,
                'fee_amount': float(tx.get('gasUsed', 0)) * float(tx.get('gasPrice', 0)) / 1e18,
                'fee_asset': 'BNB',
                'notes': f"BSC tx: {tx['hash']}"
            }
        except Exception as e:
            logger.error(f"Error processing BSC transaction: {e}")
            return None
    
    def _process_polygon_transaction(self, tx: Dict, address: str) -> Optional[Dict]:
        """Process Polygon transaction into standard format."""
        try:
            timestamp = datetime.fromtimestamp(int(tx['timeStamp']))
            
            if tx['from'].lower() == address.lower():
                tx_type = 'sell'
                base_amount = float(tx['value']) / 1e18
                quote_amount = float(tx.get('gasUsed', 0)) * float(tx.get('gasPrice', 0)) / 1e18
            else:
                tx_type = 'buy'
                base_amount = float(tx['value']) / 1e18
                quote_amount = 0
            
            return {
                'timestamp': timestamp.isoformat(),
                'type': tx_type,
                'base_asset': 'MATIC',
                'base_amount': base_amount,
                'quote_asset': 'MATIC',
                'quote_amount': quote_amount,
                'fee_amount': float(tx.get('gasUsed', 0)) * float(tx.get('gasPrice', 0)) / 1e18,
                'fee_asset': 'MATIC',
                'notes': f"Polygon tx: {tx['hash']}"
            }
        except Exception as e:
            logger.error(f"Error processing Polygon transaction: {e}")
            return None
    
    def _is_in_date_range(self, timestamp: datetime, start_date: Optional[datetime], 
                         end_date: Optional[datetime]) -> bool:
        """Check if timestamp is within date range."""
        if start_date and timestamp < start_date:
            return False
        if end_date and timestamp > end_date:
            return False
        return True
    
    def import_wallet_data(self, wallet_address: str, blockchain: str, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Import wallet data from specified blockchain.
        
        Args:
            wallet_address: Wallet address to import
            blockchain: Blockchain type ('ethereum', 'bitcoin', 'bsc', 'polygon')
            start_date: Start date for transactions (optional)
            end_date: End date for transactions (optional)
            
        Returns:
            DataFrame with normalized transaction data
        """
        blockchain = blockchain.lower()
        
        if blockchain == 'ethereum':
            return self.import_ethereum_transactions(wallet_address, start_date, end_date)
        elif blockchain == 'bitcoin':
            return self.import_bitcoin_transactions(wallet_address, start_date, end_date)
        elif blockchain == 'bsc':
            return self.import_bsc_transactions(wallet_address, start_date, end_date)
        elif blockchain == 'polygon':
            return self.import_polygon_transactions(wallet_address, start_date, end_date)
        else:
            logger.error(f"Unsupported blockchain: {blockchain}")
            return pd.DataFrame()


def import_blockchain_data(wallet_address: str, blockchain: str, 
                          output_file: str = 'output/blockchain_import.csv',
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> pd.DataFrame:
    """
    Convenience function to import blockchain data.
    
    Args:
        wallet_address: Wallet address to import
        blockchain: Blockchain type
        output_file: Output file path
        start_date: Start date for transactions
        end_date: End date for transactions
        
    Returns:
        DataFrame with imported transactions
    """
    importer = BlockchainImporter()
    
    # Set API keys from environment variables
    import os
    importer.etherscan_api_key = os.getenv('ETHERSCAN_API_KEY')
    importer.bitcoin_api_key = os.getenv('BITCOIN_API_KEY')
    
    # Import data
    df = importer.import_wallet_data(wallet_address, blockchain, start_date, end_date)
    
    if not df.empty:
        # Save to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_csv(output_file, index=False)
        logger.info(f"Imported {len(df)} transactions from {blockchain} to {output_file}")
    else:
        logger.warning(f"No transactions found for address {wallet_address} on {blockchain}")
    
    return df
