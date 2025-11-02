"""Data normalization module for converting exchange-specific formats to standard format."""

import pandas as pd
from dateutil import parser
import logging
import os
from typing import Optional, Dict, Any
import openpyxl

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import load_exchange_mappings, config
from price_fetch import fetch_price
from ml_mapper import ColumnMapper


# Set up logging
logging.basicConfig(
    level=getattr(logging, config.get('app', 'log_level', 'INFO')),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def normalize_csv(
    input_file: str,
    exchange: str,
    output_file: str = 'output/normalized.csv',
    remove_duplicates: bool = False,
    fetch_missing_prices: bool = False,
    sheet_name: Optional[str] = None
) -> None:
    """
    Normalize exchange CSV/XLSX to standard transaction format.
    
    Args:
        input_file: Path to input CSV or XLSX file
        exchange: Exchange name (must be in exchanges.yaml)
        output_file: Path for output normalized CSV
        remove_duplicates: Whether to remove duplicate transactions
        fetch_missing_prices: Whether to fetch missing price data
        sheet_name: Sheet name for XLSX files (default: first sheet)
    """
    # Load exchange mappings
    try:
        exchange_mappings = load_exchange_mappings()
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Failed to load exchange mappings: {e}")
        raise
    
    use_ml_only = False
    if exchange not in exchange_mappings:
        if exchange in ['unknown', 'auto', 'ml']:
            mapping = {}
            use_ml_only = True
        else:
            raise ValueError(f"Unsupported exchange: {exchange}. Add to config/exchanges.yaml.")
    else:
        mapping = exchange_mappings[exchange]
    
    # Read input file with memory optimization
    try:
        if input_file.endswith('.xlsx'):
            df = pd.read_excel(input_file, sheet_name=sheet_name or 0)
        else:
            # Use chunking for large CSV files
            file_size = os.path.getsize(input_file)
            if file_size > 50 * 1024 * 1024:  # 50MB
                logger.info(f"Large file detected ({file_size / 1024 / 1024:.1f}MB), using chunked reading")
                chunks = []
                for chunk in pd.read_csv(input_file, chunksize=10000):
                    chunks.append(chunk)
                df = pd.concat(chunks, ignore_index=True)
            else:
                df = pd.read_csv(input_file)
        
        if df.empty:
            raise ValueError("Input file is empty or has no data.")
            
        logger.info(f"Loaded {len(df)} rows from {input_file}")
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_file}")
    except ValueError as e:
        if "sheet" in str(e).lower():
            logger.error(f"Sheet error: {e}")
            raise RuntimeError(f"Invalid sheet: {sheet_name}")
        raise
    except Exception as e:
        logger.error(f"File read error: {e}")
        raise RuntimeError(f"Error reading file: {e}")
    
    rename_dict = {}
    _seen_sources = set()
    for k, v in mapping.items():
        if k not in ['unique_columns', 'signature_patterns', 'required_columns'] and v is not None and v != 'None' and isinstance(v, str):
            if v in _seen_sources:
                continue
            rename_dict[v] = k
            _seen_sources.add(v)
    std_labels = [
        'timestamp', 'type', 'base_asset', 'base_amount',
        'quote_asset', 'quote_amount', 'fee_amount', 'fee_asset', 'notes'
    ]
    missing_cols = [v for v in rename_dict if v not in df.columns]
    if missing_cols:
        logger.warning(f"Missing columns in input: {missing_cols}. Using None for mapping.")
    try:
        mapper = ColumnMapper()
        mapper.load_or_fit()
        ml_map = mapper.predict_mapping(list(df.columns), threshold=0.8)
        combined = dict(rename_dict)
        used = set(combined.values())
        for col, (lbl, prob) in ml_map.items():
            if col not in combined and lbl in std_labels and lbl not in used:
                combined[col] = lbl
                used.add(lbl)
        rename_dict = combined
    except Exception as e:
        logger.debug(f"ML mapper unavailable: {e}")
    df = df.rename(columns=rename_dict)
    need_base = 'base_asset' not in df.columns or df['base_asset'].isna().all()
    need_quote = 'quote_asset' not in df.columns or df['quote_asset'].isna().all()
    if need_base or need_quote:
        if 'base_asset' not in df.columns:
            df['base_asset'] = None
        if 'quote_asset' not in df.columns:
            df['quote_asset'] = None
        candidates = []
        for c in df.columns:
            cl = c.lower()
            if c in ['base_asset','quote_asset']:
                continue
            if any(k in cl for k in ['pair','market','symbol','instrument','product','book','currency_pair','currency pair','ticker']):
                candidates.append(c)
        best_col = None
        best_score = 0.0
        for c in candidates:
            srs = df[c].dropna().astype(str)
            if srs.empty:
                continue
            sample = srs.head(80)
            ok = 0
            total = 0
            for v in sample:
                b,q = parse_pair(v)
                if b or q:
                    ok += 1
                total += 1
            score = ok/total if total else 0
            if score > best_score:
                best_score = score
                best_col = c
        if best_col and best_score >= 0.5:
            pair_df = df[best_col].apply(parse_pair).apply(pd.Series)
            pair_df.columns = ['__pair_base','__pair_quote']
            if df['base_asset'].isna().any():
                df['base_asset'] = df['base_asset'].fillna(pair_df['__pair_base'])
            if df['quote_asset'].isna().any():
                df['quote_asset'] = df['quote_asset'].fillna(pair_df['__pair_quote'])
    
    # Handle fee_asset default
    if mapping.get('fee_asset') in [None, 'None'] and 'quote_asset' in df.columns:
        df['fee_asset'] = df['quote_asset']
    
    # Parse trading pairs if needed
    if 'base_asset' in df.columns and exchange in ['kraken', 'bitfinex', 'bitstamp', 'bittrex', 'htx']:
        df[['base_asset', 'quote_asset']] = df['base_asset'].apply(parse_pair).apply(pd.Series)
    for c in ['base_asset','quote_asset','fee_asset']:
        if c in df.columns:
            df[c] = df[c].apply(lambda x: str(x).strip().upper() if pd.notna(x) else x)
    
    # Parse timestamps
    if 'timestamp' in df.columns:
        def _safe_parse_ts(x):
            if pd.isna(x):
                return None
            s = str(x).strip()
            if s == '' or s.lower() in ['na', 'n/a', 'none', 'null', '-']:
                return None
            try:
                return parser.parse(s).isoformat()
            except Exception:
                try:
                    ts = pd.to_datetime(s, errors='coerce', dayfirst=True)
                    return ts.isoformat() if not pd.isna(ts) else None
                except Exception:
                    return None
        df['timestamp'] = df['timestamp'].apply(_safe_parse_ts)
    
    # Convert numeric columns
    numeric_cols = ['base_amount', 'quote_amount', 'fee_amount']
    for col in numeric_cols:
        if col in df.columns:
            def _parse_number(x):
                if pd.isna(x):
                    return 0
                s = str(x).strip()
                if s == '' or s.lower() in ['na', 'n/a', 'none', 'null', '-']:
                    return 0
                neg = False
                if s.startswith('(') and s.endswith(')'):
                    neg = True
                    s = s[1:-1]
                for ch in ['$','€','£','¥','₿']:
                    s = s.replace(ch, '')
                s = s.replace(' ', '')
                if s.count('.') == 0 and s.count(',') == 1:
                    s = s.replace(',', '.')
                s = s.replace(',', '')
                try:
                    val = float(s)
                    return -val if neg else val
                except Exception:
                    try:
                        return float(s.replace("'", ''))
                    except Exception:
                        return 0
            df[col] = df[col].apply(_parse_number)
    
    # Fetch missing prices if requested
    if fetch_missing_prices and 'quote_amount' in df.columns:
        _fetch_missing_prices(df)
    
    # Validate transaction types
    if 'type' in df.columns:
        _validate_transaction_types(df)
    
    # Ensure all standard columns exist
    standard_cols = [
        'timestamp', 'type', 'base_asset', 'base_amount', 
        'quote_asset', 'quote_amount', 'fee_amount', 'fee_asset', 'notes'
    ]
    for col in standard_cols:
        if col not in df.columns:
            df[col] = None
    
    # Remove duplicates if requested
    if remove_duplicates:
        initial_count = len(df)
        df = df.drop_duplicates(subset=['timestamp', 'type', 'base_amount', 'quote_asset'])
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate transactions")
    
    # Validate the normalized data
    from validate import validate_df
    validate_df(df)
    
    sort_cols = [c for c in ['timestamp', 'base_asset', 'type'] if c in df.columns]
    if sort_cols:
        try:
            df = df.sort_values(sort_cols, kind='mergesort').reset_index(drop=True)
        except Exception as e:
            logger.warning(f"Sorting failed: {e}")

    # Save normalized CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df[standard_cols].to_csv(output_file, index=False)
    
    logger.info(f"Normalized CSV saved to {output_file}")
    print(f"Normalized CSV saved to {output_file}")


def parse_pair(pair: str) -> tuple:
    """
    Parse trading pair string to extract base and quote assets.
    
    Args:
        pair: Trading pair string (e.g., 'BTC/USD', 'BTCUSD', 'XBTUSD')
        
    Returns:
        Tuple of (base_asset, quote_asset)
    """
    if pd.isna(pair) or not pair:
        return None, None
    
    pair = str(pair).strip()
    
    # Remove Kraken's X/Z prefixes
    if pair.startswith('X') or pair.startswith('Z'):
        pair = pair[1:]
    
    # Try different separators
    for sep in ['/', '-', '_']:
        if sep in pair:
            parts = pair.split(sep, 1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
    
    # Handle common patterns without separators
    common_quotes = ['USD', 'USDT', 'USDC', 'EUR', 'GBP', 'BTC', 'ETH']
    for quote in common_quotes:
        if pair.endswith(quote) and len(pair) > len(quote):
            base = pair[:-len(quote)]
            return base, quote
    
    # If no pattern matches, return the pair as base asset
    return pair, None


def _fetch_missing_prices(df: pd.DataFrame) -> None:
    """Fetch missing price data for transactions with zero quote_amount."""
    mask = (df['quote_amount'] == 0) | df['quote_amount'].isna()
    missing_count = mask.sum()
    
    if missing_count == 0:
        return
    
    logger.info(f"Fetching prices for {missing_count} transactions with missing price data")
    
    for idx in df[mask].index:
        row = df.loc[idx]
        if pd.isna(row['base_asset']) or pd.isna(row['timestamp']):
            continue
            
        try:
            price = fetch_price(
                row['base_asset'], 
                pd.to_datetime(row['timestamp']), 
                row.get('quote_asset', 'usd')
            )
            if price:
                df.at[idx, 'quote_amount'] = price * row['base_amount']
                logger.debug(f"Fetched price for {row['base_asset']}: {price}")
            else:
                logger.warning(f"Could not fetch price for {row['base_asset']} at {row['timestamp']}")
        except Exception as e:
            logger.warning(f"Price fetch failed for {row['base_asset']}: {e}")


def _validate_transaction_types(df: pd.DataFrame) -> None:
    """Validate and warn about unknown transaction types."""
    if 'type' not in df.columns:
        return
    
    known_types = ['buy', 'sell', 'deposit', 'withdraw', 'stake', 'airdrop', 'transfer', 'fee']
    df['type'] = df['type'].str.lower()
    
    unknown_mask = ~df['type'].isin(known_types)
    unknown_types = df[unknown_mask]['type'].unique()
    
    if len(unknown_types) > 0:
        logger.warning(f"Unknown transaction types found: {list(unknown_types)}. May affect tax calculations.")