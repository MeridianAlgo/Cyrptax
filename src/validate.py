"""Data validation module for checking transaction data quality and consistency."""

import pandas as pd
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def validate_df(df: pd.DataFrame, required_cols: List[str] = None) -> Dict[str, Any]:
    """
    Validate normalized transaction DataFrame for data quality issues.
    
    Args:
        df: Normalized transaction DataFrame
        required_cols: List of required column names
        
    Returns:
        Dictionary with validation results and statistics
    """
    if required_cols is None:
        required_cols = ['timestamp', 'type', 'base_asset', 'base_amount']
    
    validation_results = {
        'total_transactions': len(df),
        'errors': [],
        'warnings': [],
        'duplicates_found': 0,
        'negative_balances': [],
        'invalid_dates': 0,
        'missing_data': {}
    }
    
    # Check required columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        error_msg = f"Missing required columns: {missing_cols}"
        validation_results['errors'].append(error_msg)
        logger.error(error_msg)
        return validation_results
    
    # Check for duplicates
    duplicates = check_duplicates(df)
    validation_results['duplicates_found'] = duplicates
    
    # Check for negative amounts in buy/deposit transactions
    negative_amounts = check_negative_amounts(df)
    if negative_amounts > 0:
        warning_msg = f"Found {negative_amounts} transactions with negative amounts in buys/deposits"
        validation_results['warnings'].append(warning_msg)
        logger.warning(warning_msg)
    
    # Check for negative balances
    negative_balances = check_balances(df)
    validation_results['negative_balances'] = negative_balances
    
    # Check date validity
    invalid_dates = check_date_validity(df)
    validation_results['invalid_dates'] = invalid_dates
    
    # Check for missing critical data
    missing_data = check_missing_data(df)
    validation_results['missing_data'] = missing_data
    
    # Check data types
    type_issues = check_data_types(df)
    if type_issues:
        validation_results['warnings'].extend(type_issues)
    
    # Log summary
    if validation_results['errors']:
        logger.error(f"Validation failed with {len(validation_results['errors'])} errors")
    elif validation_results['warnings']:
        logger.warning(f"Validation completed with {len(validation_results['warnings'])} warnings")
    else:
        logger.info("Data validation passed successfully")
    
    return validation_results


def check_duplicates(df: pd.DataFrame) -> int:
    """
    Check for duplicate transactions.
    
    Args:
        df: Transaction DataFrame
        
    Returns:
        Number of duplicate transactions found
    """
    # Define columns to check for duplicates
    duplicate_cols = ['timestamp', 'type', 'base_asset', 'base_amount']
    available_cols = [col for col in duplicate_cols if col in df.columns]
    
    if len(available_cols) < 3:
        logger.warning("Insufficient columns for duplicate detection")
        return 0
    
    duplicates = df.duplicated(subset=available_cols).sum()
    
    if duplicates > 0:
        logger.warning(f"Found {duplicates} potential duplicate transactions")
        
        # Log details of duplicates for debugging
        duplicate_rows = df[df.duplicated(subset=available_cols, keep=False)]
        for _, row in duplicate_rows.head(5).iterrows():  # Show first 5 duplicates
            logger.debug(f"Duplicate: {row[available_cols].to_dict()}")
    
    return duplicates


def check_negative_amounts(df: pd.DataFrame) -> int:
    """
    Check for negative amounts in buy/deposit transactions.
    
    Args:
        df: Transaction DataFrame
        
    Returns:
        Number of transactions with negative amounts in buys/deposits
    """
    if 'type' not in df.columns or 'base_amount' not in df.columns:
        return 0
    
    buy_deposit_mask = df['type'].str.lower().isin(['buy', 'deposit', 'stake', 'airdrop'])
    negative_mask = df['base_amount'] < 0
    
    negative_count = (buy_deposit_mask & negative_mask).sum()
    
    if negative_count > 0:
        logger.warning(f"Found {negative_count} buy/deposit transactions with negative amounts")
    
    return negative_count


def check_balances(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Check for negative balances by tracking each asset over time.
    
    Args:
        df: Transaction DataFrame
        
    Returns:
        List of assets and timestamps where negative balances occurred
    """
    if not all(col in df.columns for col in ['base_asset', 'base_amount', 'type', 'timestamp']):
        logger.warning("Insufficient columns for balance checking")
        return []
    
    negative_balances = []
    
    # Process each asset separately
    for asset in df['base_asset'].dropna().unique():
        asset_df = df[df['base_asset'] == asset].copy()
        
        # Sort by timestamp
        asset_df = asset_df.sort_values('timestamp')
        
        balance = 0.0
        
        for _, row in asset_df.iterrows():
            transaction_type = str(row['type']).lower()
            amount = float(row['base_amount']) if pd.notna(row['base_amount']) else 0
            
            # Update balance based on transaction type
            if transaction_type in ['buy', 'deposit', 'stake', 'airdrop', 'transfer_in']:
                balance += amount
            elif transaction_type in ['sell', 'withdraw', 'transfer_out', 'fee']:
                balance -= amount
            
            # Check for negative balance
            if balance < -1e-8:  # Small tolerance for floating point errors
                negative_balances.append({
                    'asset': asset,
                    'timestamp': row['timestamp'],
                    'balance': balance,
                    'transaction_type': transaction_type,
                    'amount': amount
                })
                logger.warning(f"Negative balance for {asset} at {row['timestamp']}: {balance}")
    
    return negative_balances


def check_date_validity(df: pd.DataFrame) -> int:
    """
    Check for invalid or unreasonable dates.
    
    Args:
        df: Transaction DataFrame
        
    Returns:
        Number of invalid dates found
    """
    if 'timestamp' not in df.columns:
        return 0
    
    invalid_count = 0
    current_date = datetime.now()
    min_reasonable_date = datetime(2009, 1, 1)  # Bitcoin genesis block
    
    for idx, timestamp in df['timestamp'].items():
        if pd.isna(timestamp):
            invalid_count += 1
            continue
        
        try:
            if isinstance(timestamp, str):
                date = pd.to_datetime(timestamp)
            else:
                date = timestamp
            
            # Check if date is reasonable
            if date < min_reasonable_date or date > current_date + timedelta(days=1):
                invalid_count += 1
                logger.warning(f"Unreasonable date found: {date}")
                
        except (ValueError, TypeError):
            invalid_count += 1
            logger.warning(f"Invalid date format: {timestamp}")
    
    return invalid_count


def check_missing_data(df: pd.DataFrame) -> Dict[str, int]:
    """
    Check for missing critical data in transactions.
    
    Args:
        df: Transaction DataFrame
        
    Returns:
        Dictionary with counts of missing data by column
    """
    critical_cols = ['timestamp', 'type', 'base_asset', 'base_amount']
    missing_data = {}
    
    for col in critical_cols:
        if col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                missing_data[col] = missing_count
                logger.warning(f"Missing {col} in {missing_count} transactions")
    
    return missing_data


def check_data_types(df: pd.DataFrame) -> List[str]:
    """
    Check for data type issues in numeric columns.
    
    Args:
        df: Transaction DataFrame
        
    Returns:
        List of data type warnings
    """
    warnings = []
    
    # Check numeric columns
    numeric_cols = ['base_amount', 'quote_amount', 'fee_amount']
    
    for col in numeric_cols:
        if col not in df.columns:
            continue
        
        # Check for non-numeric values
        try:
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            non_numeric_count = numeric_series.isna().sum() - df[col].isna().sum()
            
            if non_numeric_count > 0:
                warning = f"Found {non_numeric_count} non-numeric values in {col}"
                warnings.append(warning)
                logger.warning(warning)
        
        except Exception as e:
            warning = f"Error checking data types for {col}: {e}"
            warnings.append(warning)
            logger.warning(warning)
    
    return warnings


def validate_transaction_sequence(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate the logical sequence of transactions for each asset.
    
    Args:
        df: Transaction DataFrame
        
    Returns:
        Dictionary with sequence validation results
    """
    results = {
        'sequence_errors': [],
        'orphaned_sells': [],
        'suspicious_patterns': []
    }
    
    if not all(col in df.columns for col in ['base_asset', 'type', 'timestamp']):
        return results
    
    for asset in df['base_asset'].dropna().unique():
        asset_df = df[df['base_asset'] == asset].sort_values('timestamp')
        
        has_buy_or_deposit = False
        
        for _, row in asset_df.iterrows():
            transaction_type = str(row['type']).lower()
            
            if transaction_type in ['buy', 'deposit', 'stake', 'airdrop']:
                has_buy_or_deposit = True
            elif transaction_type in ['sell', 'withdraw'] and not has_buy_or_deposit:
                results['orphaned_sells'].append({
                    'asset': asset,
                    'timestamp': row['timestamp'],
                    'type': transaction_type
                })
    
    return results