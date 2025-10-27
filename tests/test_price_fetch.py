"""Comprehensive unit tests for the price_fetch module."""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, date
import json
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from price_fetch import fetch_price, fetch_prices_batch, PriceCache
from exceptions import PriceFetchError


class TestFetchPrice:
    """Test cases for individual price fetching."""
    
    @patch('price_fetch.requests.get')
    def test_fetch_price_success(self, mock_get):
        """Test successful price fetching from CoinGecko API."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'bitcoin': {
                'usd': 50000.0
            }
        }
        mock_get.return_value = mock_response
        
        price = fetch_price('BTC', '2024-01-01', 'usd')
        
        assert price == 50000.0
        mock_get.assert_called_once()
        
        # Verify API call parameters
        call_args = mock_get.call_args
        assert 'coingecko.com' in call_args[0][0]
        assert 'bitcoin' in call_args[0][0]
        assert '01-01-2024' in call_args[0][0]
    
    @patch('price_fetch.requests.get')
    def test_fetch_price_api_error(self, mock_get):
        """Test handling of API errors."""
        # Mock API error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not found")
        mock_get.return_value = mock_response
        
        with pytest.raises(PriceFetchError):
            fetch_price('INVALID', '2024-01-01', 'usd')
    
    @patch('price_fetch.requests.get')
    def test_fetch_price_network_error(self, mock_get):
        """Test handling of network errors."""
        # Mock network error
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(PriceFetchError):
            fetch_price('BTC', '2024-01-01', 'usd')
    
    @patch('price_fetch.requests.get')
    def test_fetch_price_invalid_response(self, mock_get):
        """Test handling of invalid API response format."""
        # Mock invalid response format
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'invalid': 'format'
        }
        mock_get.return_value = mock_response
        
        with pytest.raises(PriceFetchError):
            fetch_price('BTC', '2024-01-01', 'usd')
    
    @patch('price_fetch.requests.get')
    def test_fetch_price_rate_limiting(self, mock_get):
        """Test rate limiting behavior."""
        # Mock rate limit response
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = Exception("Rate limited")
        mock_get.return_value = mock_response
        
        with pytest.raises(PriceFetchError):
            fetch_price('BTC', '2024-01-01', 'usd')
    
    def test_fetch_price_invalid_inputs(self):
        """Test handling of invalid input parameters."""
        # Test invalid asset
        with pytest.raises((ValueError, PriceFetchError)):
            fetch_price('', '2024-01-01', 'usd')
        
        # Test invalid date
        with pytest.raises((ValueError, PriceFetchError)):
            fetch_price('BTC', 'invalid-date', 'usd')
        
        # Test invalid currency
        with pytest.raises((ValueError, PriceFetchError)):
            fetch_price('BTC', '2024-01-01', '')
    
    @patch('price_fetch.requests.get')
    def test_fetch_price_different_currencies(self, mock_get):
        """Test fetching prices in different currencies."""
        currencies = ['usd', 'eur', 'gbp', 'jpy']
        
        for currency in currencies:
            # Mock response for each currency
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'bitcoin': {
                    currency: 50000.0
                }
            }
            mock_get.return_value = mock_response
            
            price = fetch_price('BTC', '2024-01-01', currency)
            assert price == 50000.0
    
    @patch('price_fetch.requests.get')
    def test_fetch_price_different_assets(self, mock_get):
        """Test fetching prices for different cryptocurrency assets."""
        assets = ['BTC', 'ETH', 'ADA', 'DOT']
        expected_ids = ['bitcoin', 'ethereum', 'cardano', 'polkadot']
        
        for asset, expected_id in zip(assets, expected_ids):
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                expected_id: {
                    'usd': 1000.0
                }
            }
            mock_get.return_value = mock_response
            
            price = fetch_price(asset, '2024-01-01', 'usd')
            assert price == 1000.0
            
            # Verify correct CoinGecko ID was used
            call_args = mock_get.call_args
            assert expected_id in call_args[0][0]


class TestFetchPricesBatch:
    """Test cases for batch price fetching."""
    
    @patch('price_fetch.fetch_price')
    def test_fetch_prices_batch_success(self, mock_fetch_price):
        """Test successful batch price fetching."""
        # Mock individual price fetches
        mock_fetch_price.side_effect = [50000.0, 3000.0, 1.0]
        
        requests = [
            ('BTC', '2024-01-01', 'usd'),
            ('ETH', '2024-01-01', 'usd'),
            ('ADA', '2024-01-01', 'usd')
        ]
        
        results = fetch_prices_batch(requests)
        
        assert len(results) == 3
        assert results[0] == 50000.0
        assert results[1] == 3000.0
        assert results[2] == 1.0
        
        # Verify all requests were made
        assert mock_fetch_price.call_count == 3
    
    @patch('price_fetch.fetch_price')
    @patch('price_fetch.time.sleep')
    def test_fetch_prices_batch_with_delays(self, mock_sleep, mock_fetch_price):
        """Test batch fetching with rate limiting delays."""
        mock_fetch_price.return_value = 50000.0
        
        requests = [
            ('BTC', '2024-01-01', 'usd'),
            ('ETH', '2024-01-01', 'usd')
        ]
        
        results = fetch_prices_batch(requests, delay=1.0)
        
        assert len(results) == 2
        # Should have called sleep between requests
        mock_sleep.assert_called()
    
    @patch('price_fetch.fetch_price')
    def test_fetch_prices_batch_partial_failure(self, mock_fetch_price):
        """Test batch fetching with some failures."""
        # Mock mixed success/failure
        def side_effect(*args):
            if args[0] == 'BTC':
                return 50000.0
            elif args[0] == 'INVALID':
                raise PriceFetchError("Asset not found")
            else:
                return 3000.0
        
        mock_fetch_price.side_effect = side_effect
        
        requests = [
            ('BTC', '2024-01-01', 'usd'),
            ('INVALID', '2024-01-01', 'usd'),
            ('ETH', '2024-01-01', 'usd')
        ]
        
        results = fetch_prices_batch(requests, continue_on_error=True)
        
        assert len(results) == 3
        assert results[0] == 50000.0
        assert results[1] is None  # Failed request
        assert results[2] == 3000.0
    
    def test_fetch_prices_batch_empty_requests(self):
        """Test batch fetching with empty request list."""
        results = fetch_prices_batch([])
        assert results == []
    
    @patch('price_fetch.fetch_price')
    def test_fetch_prices_batch_stop_on_error(self, mock_fetch_price):
        """Test batch fetching that stops on first error."""
        mock_fetch_price.side_effect = [50000.0, PriceFetchError("Error"), 3000.0]
        
        requests = [
            ('BTC', '2024-01-01', 'usd'),
            ('INVALID', '2024-01-01', 'usd'),
            ('ETH', '2024-01-01', 'usd')
        ]
        
        with pytest.raises(PriceFetchError):
            fetch_prices_batch(requests, continue_on_error=False)


class TestPriceCache:
    """Test cases for price caching functionality."""
    
    def test_price_cache_init(self):
        """Test price cache initialization."""
        cache = PriceCache()
        
        assert cache.cache == {}
        assert cache.cache_file is not None
    
    def test_price_cache_get_set(self):
        """Test basic cache get/set operations."""
        cache = PriceCache()
        
        # Test cache miss
        assert cache.get('BTC', '2024-01-01', 'usd') is None
        
        # Test cache set and hit
        cache.set('BTC', '2024-01-01', 'usd', 50000.0)
        assert cache.get('BTC', '2024-01-01', 'usd') == 50000.0
    
    def test_price_cache_key_generation(self):
        """Test cache key generation."""
        cache = PriceCache()
        
        # Different parameters should generate different keys
        cache.set('BTC', '2024-01-01', 'usd', 50000.0)
        cache.set('BTC', '2024-01-02', 'usd', 51000.0)
        cache.set('BTC', '2024-01-01', 'eur', 45000.0)
        cache.set('ETH', '2024-01-01', 'usd', 3000.0)
        
        assert cache.get('BTC', '2024-01-01', 'usd') == 50000.0
        assert cache.get('BTC', '2024-01-02', 'usd') == 51000.0
        assert cache.get('BTC', '2024-01-01', 'eur') == 45000.0
        assert cache.get('ETH', '2024-01-01', 'usd') == 3000.0
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_price_cache_load_from_file(self, mock_exists, mock_file):
        """Test loading cache from file."""
        # Mock file exists and contains valid JSON
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps({
            'BTC_2024-01-01_usd': 50000.0,
            'ETH_2024-01-01_usd': 3000.0
        })
        
        cache = PriceCache()
        cache.load_from_file()
        
        assert cache.get('BTC', '2024-01-01', 'usd') == 50000.0
        assert cache.get('ETH', '2024-01-01', 'usd') == 3000.0
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_price_cache_save_to_file(self, mock_exists, mock_file):
        """Test saving cache to file."""
        mock_exists.return_value = False
        
        cache = PriceCache()
        cache.set('BTC', '2024-01-01', 'usd', 50000.0)
        cache.save_to_file()
        
        # Verify file was written
        mock_file.assert_called()
        written_data = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        
        # Should contain the cached data
        assert 'BTC_2024-01-01_usd' in written_data
        assert '50000' in written_data
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_price_cache_corrupted_file(self, mock_exists, mock_file):
        """Test handling of corrupted cache file."""
        # Mock file exists but contains invalid JSON
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = "invalid json"
        
        cache = PriceCache()
        
        # Should handle corrupted file gracefully
        cache.load_from_file()
        assert cache.cache == {}
    
    def test_price_cache_clear(self):
        """Test cache clearing functionality."""
        cache = PriceCache()
        
        # Add some data
        cache.set('BTC', '2024-01-01', 'usd', 50000.0)
        cache.set('ETH', '2024-01-01', 'usd', 3000.0)
        
        assert len(cache.cache) == 2
        
        # Clear cache
        cache.clear()
        assert len(cache.cache) == 0
        assert cache.get('BTC', '2024-01-01', 'usd') is None


class TestPriceFetchIntegration:
    """Integration tests for price fetching workflow."""
    
    @patch('price_fetch.requests.get')
    @patch('price_fetch.PriceCache')
    def test_fetch_price_with_caching(self, mock_cache_class, mock_get):
        """Test price fetching with caching integration."""
        # Mock cache
        mock_cache = MagicMock()
        mock_cache.get.return_value = None  # Cache miss
        mock_cache_class.return_value = mock_cache
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'bitcoin': {
                'usd': 50000.0
            }
        }
        mock_get.return_value = mock_response
        
        price = fetch_price('BTC', '2024-01-01', 'usd')
        
        assert price == 50000.0
        
        # Verify cache was checked and updated
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once_with('BTC', '2024-01-01', 'usd', 50000.0)
    
    @patch('price_fetch.PriceCache')
    def test_fetch_price_cache_hit(self, mock_cache_class):
        """Test price fetching with cache hit (no API call)."""
        # Mock cache hit
        mock_cache = MagicMock()
        mock_cache.get.return_value = 50000.0  # Cache hit
        mock_cache_class.return_value = mock_cache
        
        with patch('price_fetch.requests.get') as mock_get:
            price = fetch_price('BTC', '2024-01-01', 'usd')
            
            assert price == 50000.0
            
            # Should not make API call
            mock_get.assert_not_called()
    
    @patch('price_fetch.fetch_price')
    def test_real_world_batch_scenario(self, mock_fetch_price):
        """Test realistic batch price fetching scenario."""
        # Mock prices for different assets and dates
        price_map = {
            ('BTC', '2024-01-01'): 45000.0,
            ('BTC', '2024-01-02'): 46000.0,
            ('ETH', '2024-01-01'): 2800.0,
            ('ETH', '2024-01-02'): 2850.0,
            ('ADA', '2024-01-01'): 0.5,
            ('ADA', '2024-01-02'): 0.52
        }
        
        def mock_price_fetch(asset, date, currency):
            return price_map.get((asset, date), 1000.0)
        
        mock_fetch_price.side_effect = mock_price_fetch
        
        # Simulate transaction data requiring prices
        requests = [
            ('BTC', '2024-01-01', 'usd'),
            ('BTC', '2024-01-02', 'usd'),
            ('ETH', '2024-01-01', 'usd'),
            ('ETH', '2024-01-02', 'usd'),
            ('ADA', '2024-01-01', 'usd'),
            ('ADA', '2024-01-02', 'usd')
        ]
        
        results = fetch_prices_batch(requests)
        
        assert len(results) == 6
        assert results[0] == 45000.0  # BTC 2024-01-01
        assert results[1] == 46000.0  # BTC 2024-01-02
        assert results[2] == 2800.0   # ETH 2024-01-01
        assert results[3] == 2850.0   # ETH 2024-01-02
        assert results[4] == 0.5      # ADA 2024-01-01
        assert results[5] == 0.52     # ADA 2024-01-02


class TestPriceFetchErrorHandling:
    """Test error handling in price fetching."""
    
    def test_invalid_asset_mapping(self):
        """Test handling of assets not supported by CoinGecko."""
        with pytest.raises((ValueError, PriceFetchError)):
            fetch_price('UNKNOWN_ASSET', '2024-01-01', 'usd')
    
    @patch('price_fetch.requests.get')
    def test_api_timeout(self, mock_get):
        """Test handling of API timeouts."""
        mock_get.side_effect = Exception("Timeout")
        
        with pytest.raises(PriceFetchError):
            fetch_price('BTC', '2024-01-01', 'usd')
    
    @patch('price_fetch.requests.get')
    def test_malformed_api_response(self, mock_get):
        """Test handling of malformed API responses."""
        # Mock response with unexpected structure
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'unexpected': 'structure'
        }
        mock_get.return_value = mock_response
        
        with pytest.raises(PriceFetchError):
            fetch_price('BTC', '2024-01-01', 'usd')
    
    def test_date_format_validation(self):
        """Test validation of date formats."""
        invalid_dates = [
            '2024/01/01',  # Wrong separator
            '01-01-2024',  # Wrong order
            '2024-13-01',  # Invalid month
            '2024-01-32',  # Invalid day
            'not-a-date'   # Not a date
        ]
        
        for invalid_date in invalid_dates:
            with pytest.raises((ValueError, PriceFetchError)):
                fetch_price('BTC', invalid_date, 'usd')


class TestPriceFetchPerformance:
    """Performance tests for price fetching."""
    
    @patch('price_fetch.fetch_price')
    def test_batch_performance(self, mock_fetch_price):
        """Test performance of batch price fetching."""
        mock_fetch_price.return_value = 50000.0
        
        # Large batch of requests
        requests = [('BTC', f'2024-01-{i:02d}', 'usd') for i in range(1, 32)]  # 31 days
        
        start_time = time.time()
        results = fetch_prices_batch(requests, delay=0.01)  # Minimal delay for testing
        end_time = time.time()
        
        assert len(results) == 31
        assert all(price == 50000.0 for price in results)
        
        # Should complete within reasonable time
        processing_time = end_time - start_time
        assert processing_time < 5.0  # Adjust threshold as needed
    
    def test_cache_performance(self):
        """Test cache performance with many operations."""
        cache = PriceCache()
        
        # Add many entries
        start_time = time.time()
        for i in range(1000):
            cache.set('BTC', f'2024-01-01-{i}', 'usd', 50000.0 + i)
        end_time = time.time()
        
        set_time = end_time - start_time
        
        # Retrieve many entries
        start_time = time.time()
        for i in range(1000):
            price = cache.get('BTC', f'2024-01-01-{i}', 'usd')
            assert price == 50000.0 + i
        end_time = time.time()
        
        get_time = end_time - start_time
        
        # Cache operations should be fast
        assert set_time < 1.0
        assert get_time < 1.0


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])