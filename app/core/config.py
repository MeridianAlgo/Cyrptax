"""Configuration management for the crypto tax tool."""

import configparser
import os
import yaml
from typing import Dict, Any


class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_file: str = 'config/app.conf'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            # Set default values if config file doesn't exist
            self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        self.config['app'] = {
            'default_currency': 'usd',
            'default_tax_method': 'fifo',
            'log_level': 'INFO'
        }
        self.config['api'] = {
            'coingecko_base_url': 'https://api.coingecko.com/api/v3',
            'request_timeout': '30',
            'rate_limit_delay': '1.0'
        }
        self.config['processing'] = {
            'max_file_size_mb': '100',
            'batch_size': '1000',
            'cache_prices': 'true'
        }
        self.config['output'] = {
            'reports_dir': 'output/reports',
            'logs_dir': 'output/logs',
            'date_format': '%Y-%m-%d',
            'decimal_places': '8'
        }
    
    def get(self, section: str, key: str, fallback: Any = None) -> str:
        """Get configuration value."""
        return self.config.get(section, key, fallback=fallback)
    
    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """Get integer configuration value."""
        return self.config.getint(section, key, fallback=fallback)
    
    def getfloat(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get float configuration value."""
        return self.config.getfloat(section, key, fallback=fallback)
    
    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get boolean configuration value."""
        return self.config.getboolean(section, key, fallback=fallback)


def load_exchange_mappings(config_path: str = 'config/exchanges.yaml') -> Dict[str, Dict[str, str]]:
    """Load exchange field mappings from YAML file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Exchange mappings file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing exchange mappings YAML: {e}")


# Global configuration instance
config = Config()