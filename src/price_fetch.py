"""Price fetching module for retrieving historical cryptocurrency prices."""

import requests
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
import os
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config

logger = logging.getLogger(__name__)


class PriceFetcher:
    """Handles fetching and caching of cryptocurrency prices."""
    
    def __init__(self):
        self.base_url = config.get('api', 'coingecko_base_url', 'https://api.coingecko.com/api/v3')
        self.timeout = config.getint('api', 'request_timeout', 30)
        self.rate_limit_delay = config.getfloat('api', 'rate_limit_delay', 1.0)
        self.cache_enabled = config.getboolean('processing', 'cache_prices', True)
        self.cache_dir = Path('output/cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.last_request_time = 0
        
        # Asset ID mapping for CoinGecko
        self.asset_id_map = self._load_asset_id_map()
    
    def _load_asset_id_map(self) -> Dict[str, str]:
        """Load mapping of asset symbols to CoinGecko IDs."""
        # Common mappings - in production, this could be loaded from a file
        return {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'LINK': 'chainlink',
            'LTC': 'litecoin',
            'BCH': 'bitcoin-cash',
            'XRP': 'ripple',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'MATIC': 'matic-network',
            'AVAX': 'avalanche-2',
            'ATOM': 'cosmos',
            'UNI': 'uniswap',
            'AAVE': 'aave',
            'COMP': 'compound-governance-token',
            'MKR': 'maker',
            'SNX': 'havven',
            'YFI': 'yearn-finance',
            'SUSHI': 'sushi',
            'CRV': 'curve-dao-token',
            'BAL': 'balancer',
            'USDT': 'tether',
            'USDC': 'usd-coin',
            'DAI': 'dai',
            'BUSD': 'binance-usd'
        }
    
    def fetch_price(self, asset: str, date: datetime, vs_currency: str = 'usd') -> Optional[float]:
        """
        Fetch historical price for an asset on a specific date.
        
        Args:
            asset: Asset symbol (e.g., 'BTC', 'ETH')
            date: Date for price lookup
            vs_currency: Currency to get price in (default: 'usd')
            
        Returns:
            Price as float, or None if not found
        """
        # Check cache first
        if self.cache_enabled:
            cached_price = self._get_cached_price(asset, date, vs_currency)
            if cached_price is not None:
                return cached_price
        
        # Get CoinGecko asset ID
        asset_id = self._get_asset_id(asset)
        if not asset_id:
            logger.warning(f"No CoinGecko ID mapping found for asset: {asset}")
            return None
        
        # Rate limiting
        self._rate_limit()
        
        try:
            # Format date for CoinGecko API
            date_str = date.strftime('%d-%m-%Y')
            
            # Make API request
            url = f"{self.base_url}/coins/{asset_id}/history"
            params = {
                'date': date_str,
                'localization': 'false'
            }
            
            logger.debug(f"Fetching price for {asset} ({asset_id}) on {date_str}")
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract price from response
            if 'market_data' in data and 'current_price' in data['market_data']:
                price = data['market_data']['current_price'].get(vs_currency.lower())
                
                if price is not None:
                    # Cache the price
                    if self.cache_enabled:
                        self._cache_price(asset, date, vs_currency, price)
                    
                    logger.debug(f"Fetched price for {asset}: {price} {vs_currency.upper()}")
                    return float(price)
            
            logger.warning(f"No price data found for {asset} on {date_str}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {asset}: {e}")
            return None
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing price data for {asset}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching price for {asset}: {e}")
            return None
    
    def batch_fetch_prices(self, requests_list: list) -> Dict[str, Optional[float]]:
        """
        Fetch multiple prices efficiently.
        
        Args:
            requests_list: List of (asset, date, vs_currency) tuples
            
        Returns:
            Dictionary mapping request keys to prices
        """
        results = {}
        
        for asset, date, vs_currency in requests_list:
            key = f"{asset}_{date.strftime('%Y-%m-%d')}_{vs_currency}"
            price = self.fetch_price(asset, date, vs_currency)
            results[key] = price
            
            # Add delay between requests to respect rate limits
            time.sleep(self.rate_limit_delay)
        
        return results
    
    def _get_asset_id(self, asset: str) -> Optional[str]:
        """Get CoinGecko asset ID for a given symbol."""
        asset = asset.upper()
        
        # Check direct mapping first
        if asset in self.asset_id_map:
            return self.asset_id_map[asset]
        
        # For unknown assets, try using lowercase symbol as ID
        # This works for many assets but not all
        return asset.lower()
    
    def _rate_limit(self) -> None:
        """Implement rate limiting for API requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_cache_path(self, asset: str, date: datetime, vs_currency: str) -> Path:
        """Get cache file path for a price request."""
        date_str = date.strftime('%Y-%m-%d')
        filename = f"{asset}_{date_str}_{vs_currency}.json"
        return self.cache_dir / filename
    
    def _get_cached_price(self, asset: str, date: datetime, vs_currency: str) -> Optional[float]:
        """Retrieve price from cache if available."""
        cache_path = self._get_cache_path(asset, date, vs_currency)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid (within 24 hours for historical data)
            cache_time = datetime.fromisoformat(cache_data['cached_at'])
            if datetime.now() - cache_time > timedelta(hours=24):
                return None
            
            return cache_data['price']
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
            return None
    
    def _cache_price(self, asset: str, date: datetime, vs_currency: str, price: float) -> None:
        """Cache a fetched price."""
        cache_path = self._get_cache_path(asset, date, vs_currency)
        
        cache_data = {
            'asset': asset,
            'date': date.isoformat(),
            'vs_currency': vs_currency,
            'price': price,
            'cached_at': datetime.now().isoformat()
        }
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to cache price for {asset}: {e}")


# Global price fetcher instance
_price_fetcher = None


def get_price_fetcher() -> PriceFetcher:
    """Get global price fetcher instance."""
    global _price_fetcher
    if _price_fetcher is None:
        _price_fetcher = PriceFetcher()
    return _price_fetcher


def fetch_price(asset: str, date: datetime, vs_currency: str = 'usd') -> Optional[float]:
    """
    Convenience function to fetch a single price.
    
    Args:
        asset: Asset symbol
        date: Date for price lookup
        vs_currency: Currency to get price in
        
    Returns:
        Price as float, or None if not found
    """
    fetcher = get_price_fetcher()
    return fetcher.fetch_price(asset, date, vs_currency)