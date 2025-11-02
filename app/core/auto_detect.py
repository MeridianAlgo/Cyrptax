"""Auto-detection module for identifying exchange formats from CSV files."""

import pandas as pd
import os
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import load_exchange_mappings

logger = logging.getLogger(__name__)


class ExchangeDetector:
    """Detects exchange format by analyzing CSV column headers and patterns."""
    
    def __init__(self):
        self.exchange_mappings = load_exchange_mappings()
        self.confidence_threshold = 0.9  # Raised to 90% for higher accuracy
    
    def detect_exchange(self, file_path: str, sheet_name: Optional[str] = None) -> Tuple[str, float, Dict]:
        """
        Detect the most likely exchange format for a given file with enhanced error handling.
        
        Args:
            file_path: Path to CSV or XLSX file
            sheet_name: Sheet name for XLSX files
            
        Returns:
            Tuple of (exchange_name, confidence_score, analysis_details)
        """
        from exceptions import FileFormatError, DataValidationError, handle_file_error
        
        try:
            # Validate file exists and is readable
            if not os.path.exists(file_path):
                raise FileFormatError(f"File not found: {file_path}", file_path=file_path)
            
            # Check file size (avoid processing huge files)
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:  # 100MB limit
                logger.warning(f"Large file detected: {file_size / 1024 / 1024:.1f}MB")
            
            # Read file with enhanced error handling
            try:
                if file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path, sheet_name=sheet_name or 0, nrows=10)
                elif file_path.endswith('.csv'):
                    # Try different encodings
                    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                    df = None
                    for encoding in encodings:
                        try:
                            df = pd.read_csv(file_path, nrows=10, encoding=encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if df is None:
                        raise FileFormatError(f"Could not read CSV file with any encoding", 
                                            file_path=file_path, expected_format="UTF-8 CSV")
                else:
                    raise FileFormatError(f"Unsupported file format: {Path(file_path).suffix}", 
                                        file_path=file_path, expected_format="CSV or XLSX")
                
            except pd.errors.EmptyDataError:
                raise DataValidationError("File contains no data", file_path=file_path)
            except pd.errors.ParserError as e:
                raise FileFormatError(f"File parsing error: {e}", file_path=file_path)
            
            if df is None or df.empty:
                raise DataValidationError("File is empty or contains no readable data", file_path=file_path)
            
            # Validate columns
            if len(df.columns) < 3:
                raise DataValidationError(f"Insufficient columns: {len(df.columns)} (minimum 3 required)", 
                                        file_path=file_path)
            
            columns = [col.lower().strip() for col in df.columns if col and str(col).strip()]
            
            if not columns:
                raise DataValidationError("No valid column headers found", file_path=file_path)
            
            # Analyze each exchange mapping with error handling
            scores = {}
            analysis = {}
            errors = []
            
            for exchange, mapping in self.exchange_mappings.items():
                try:
                    score, details = self._calculate_match_score(columns, mapping, df)
                    scores[exchange] = score
                    analysis[exchange] = details
                except Exception as e:
                    logger.warning(f"Error analyzing {exchange}: {e}")
                    scores[exchange] = 0.0
                    analysis[exchange] = {"error": str(e)}
                    errors.append(f"{exchange}: {e}")
            
            if not scores or all(score == 0.0 for score in scores.values()):
                return "unknown", 0.0, {
                    "error": "No exchange patterns matched",
                    "columns_found": columns,
                    "analysis_errors": errors
                }
            
            # Find best match with tie-breaking
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            best_exchange = sorted_scores[0][0]
            best_score = sorted_scores[0][1]
            
            # Check for ties (multiple exchanges with similar high scores)
            ties = [ex for ex, score in sorted_scores if abs(score - best_score) < 0.05 and score > 0.5]
            
            result_details = {
                "all_scores": scores,
                "analysis": analysis[best_exchange],
                "columns_found": columns,
                "file_size_mb": file_size / 1024 / 1024,
                "rows_analyzed": len(df)
            }
            
            if len(ties) > 1:
                result_details["ties"] = ties
                result_details["warning"] = f"Multiple exchanges matched with similar confidence: {ties}"
                logger.warning(f"Tie detected for {file_path}: {ties}")
            
            logger.info(f"Auto-detection for {file_path}: {best_exchange} (confidence: {best_score:.3f})")
            
            return best_exchange, best_score, result_details
            
        except (FileFormatError, DataValidationError) as e:
            logger.error(f"Validation error for {file_path}: {e}")
            return "unknown", 0.0, {"error": str(e), "error_type": type(e).__name__}
        except Exception as e:
            logger.error(f"Unexpected error detecting exchange for {file_path}: {e}")
            return "unknown", 0.0, {"error": f"Unexpected error: {e}", "error_type": "UnexpectedError"}
    
    def _calculate_match_score(self, columns: List[str], mapping: Dict, df: pd.DataFrame) -> Tuple[float, Dict]:
        """Calculate how well columns match an exchange mapping with enhanced accuracy."""
        details = {
            "matched_columns": [],
            "missing_columns": [],
            "extra_columns": [],
            "pattern_matches": [],
            "unique_matches": [],
            "signature_matches": []
        }
        
        # Get expected columns from mapping (excluding None values and metadata)
        expected_columns = []
        unique_columns = mapping.get('unique_columns', [])
        signature_patterns = mapping.get('signature_patterns', [])
        
        for key, value in mapping.items():
            if key not in ['unique_columns', 'signature_patterns', 'required_columns'] and value and value != 'None':
                if isinstance(value, str):
                    expected_columns.append(value.lower())
                # Skip non-string values (like lists)
        
        # Enhanced column matching with weighted scoring
        matched = 0
        unique_matched = 0
        total_expected = len(expected_columns)
        
        for expected_col in expected_columns:
            match_found = False
            match_weight = 1.0
            
            # Check if this is a unique identifier column (higher weight)
            if any(expected_col.lower() == unique.lower() for unique in unique_columns):
                match_weight = 2.0
            
            # Direct exact match (highest score)
            if expected_col in columns:
                matched += match_weight
                if match_weight > 1.0:
                    unique_matched += 1
                    details["unique_matches"].append(expected_col)
                details["matched_columns"].append(expected_col)
                match_found = True
            else:
                # Enhanced fuzzy matching
                for col in columns:
                    if self._enhanced_fuzzy_match(expected_col, col):
                        matched += match_weight * 0.9  # Slight penalty for fuzzy match
                        if match_weight > 1.0:
                            unique_matched += 0.9
                            details["unique_matches"].append(f"{expected_col} -> {col}")
                        details["matched_columns"].append(f"{expected_col} -> {col}")
                        match_found = True
                        break
            
            if not match_found:
                details["missing_columns"].append(expected_col)
        
        # Base score from column matching (with unique column bonus)
        max_possible_score = sum(2.0 if any(exp.lower() == unique.lower() for unique in unique_columns) else 1.0 
                                for exp in expected_columns)
        column_score = matched / max_possible_score if max_possible_score > 0 else 0
        
        # Signature pattern matching (very high weight for accuracy)
        signature_score = self._check_signature_patterns(columns, signature_patterns)
        details["signature_matches"] = signature_score
        
        # Enhanced pattern-based scoring
        pattern_score = self._enhanced_pattern_matching(columns, df, mapping)
        details["pattern_matches"] = pattern_score
        
        # Unique column bonus (if we match unique identifiers, very high confidence)
        unique_bonus = min(unique_matched / len(unique_columns), 1.0) if unique_columns else 0
        
        # Balanced weighted combination for accurate detection
        # 35% column matching, 35% signature patterns, 20% unique columns, 10% general patterns
        final_score = (column_score * 0.35) + (signature_score * 0.35) + (unique_bonus * 0.2) + (pattern_score * 0.1)
        
        # Penalty for missing critical unique columns (prevents over-matching)
        if unique_columns and unique_matched < len(unique_columns) * 0.5:
            final_score *= 0.7
        
        # Strong boost for perfect unique matches
        if unique_matched >= len(unique_columns) * 0.9 and unique_columns:
            final_score = min(final_score * 1.3, 1.0)
        elif unique_matched >= len(unique_columns) * 0.7 and unique_columns:
            final_score = min(final_score * 1.15, 1.0)
        
        # Additional boost for required columns match
        required_columns = mapping.get('required_columns', [])
        if required_columns:
            required_matched = sum(1 for req in required_columns 
                                 if any(self._enhanced_fuzzy_match(req.lower(), col) for col in columns))
            required_ratio = required_matched / len(required_columns)
            if required_ratio >= 0.9:
                final_score = min(final_score * 1.2, 1.0)
            elif required_ratio >= 0.7:
                final_score = min(final_score * 1.1, 1.0)
            elif required_ratio < 0.5:
                # Penalty for missing required columns
                final_score *= 0.8
        
        # Identify extra columns
        details["extra_columns"] = [col for col in columns if col not in expected_columns]
        
        return final_score, details
    
    def _enhanced_fuzzy_match(self, expected: str, actual: str) -> bool:
        """Enhanced fuzzy matching with better accuracy."""
        expected_clean = expected.lower().replace(' ', '').replace('_', '').replace('-', '').replace('(', '').replace(')', '')
        actual_clean = actual.lower().replace(' ', '').replace('_', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Direct exact match
        if expected_clean == actual_clean:
            return True
        
        # Direct contains match (both directions)
        if expected_clean in actual_clean or actual_clean in expected_clean:
            return True
        
        # Enhanced keyword matching with exchange-specific terms
        enhanced_keywords = {
            'timestamp': ['time', 'date', 'datetime', 'created', 'timestamp', 'when'],
            'type': ['type', 'side', 'operation', 'transaction', 'action', 'kind'],
            'asset': ['asset', 'symbol', 'currency', 'coin', 'pair', 'market', 'instrument', 'token'],
            'amount': ['amount', 'quantity', 'vol', 'size', 'filled', 'executed', 'volume', 'units'],
            'price': ['price', 'rate', 'cost', 'value', 'subtotal', 'total'],
            'fee': ['fee', 'commission', 'spread', 'gas', 'trading'],
            'total': ['total', 'subtotal', 'value', 'amount'],
            'id': ['id', 'hash', 'uuid', 'order', 'tx', 'transaction'],
            'notes': ['notes', 'info', 'specification', 'remark', 'description']
        }
        
        # Check if both strings contain keywords from the same category
        for category, keywords in enhanced_keywords.items():
            expected_has_keyword = any(keyword in expected_clean for keyword in keywords)
            actual_has_keyword = any(keyword in actual_clean for keyword in keywords)
            
            if expected_has_keyword and actual_has_keyword:
                # Additional validation for better accuracy
                if category in ['timestamp', 'type', 'fee']:
                    # These are critical fields, require stronger match
                    common_words = set(expected_clean.split()) & set(actual_clean.split())
                    if len(common_words) > 0:
                        return True
                else:
                    return True
        
        # Exchange-specific pattern matching
        exchange_patterns = {
            'binance': ['base', 'quote', 'bnb'],
            'coinbase': ['transacted', 'spot', 'gdax'],
            'kraken': ['pair', 'vol', 'ledger', 'xbt', 'xeth'],
            'gemini': ['usd', 'specification'],
            'kucoin': ['filled', 'remark'],
            'bitfinex': ['description', 'bfx'],
            'okx': ['instrument', 'okex'],
            'bybit': ['change', 'coin'],
            'metamask': ['txhash', 'ethereum']
        }
        
        for exchange, patterns in exchange_patterns.items():
            if any(pattern in expected_clean for pattern in patterns) and any(pattern in actual_clean for pattern in patterns):
                return True
        
        return False
    
    def _check_signature_patterns(self, columns: List[str], signature_patterns: List[str]) -> float:
        """Check for exchange signature patterns with enhanced matching."""
        if not signature_patterns:
            return 0.0
        
        score = 0.0
        columns_text = ' '.join(columns).lower()
        total_patterns = len(signature_patterns)
        
        for pattern in signature_patterns:
            pattern_lower = pattern.lower().replace('-', '').replace('_', '').replace(' ', '')
            
            # Exact column name match (highest score)
            exact_match = any(pattern_lower == col.lower().replace('-', '').replace('_', '').replace(' ', '') 
                            for col in columns)
            if exact_match:
                score += 1.0
                continue
            
            # Direct pattern match in any column (high score)
            if any(pattern_lower in col.lower().replace('-', '').replace('_', '').replace(' ', '') 
                   for col in columns):
                score += 0.9
                continue
            
            # Pattern in combined column text (medium score)
            if pattern_lower in columns_text.replace('-', '').replace('_', '').replace(' ', ''):
                score += 0.7
                continue
            
            # Partial pattern match (low score)
            pattern_parts = [part for part in pattern_lower.split() if len(part) > 2]
            if pattern_parts and any(part in columns_text for part in pattern_parts):
                score += 0.4
        
        # Normalize and apply bonus for high match rate
        normalized_score = score / total_patterns
        
        # Bonus for matching most patterns
        if normalized_score >= 0.8:
            normalized_score = min(normalized_score * 1.2, 1.0)
        
        return normalized_score
    
    def _enhanced_pattern_matching(self, columns: List[str], df: pd.DataFrame, mapping: Dict) -> float:
        """Enhanced pattern matching for exchange identification."""
        pattern_score = 0.0
        
        # Column count patterns (exchanges have typical column counts)
        column_count_patterns = {
            'binance': (6, 10),
            'coinbase': (8, 12),
            'kraken': (6, 9),
            'gemini': (6, 8),
            'kucoin': (7, 10)
        }
        
        # Check if column count matches expected range
        for exchange, (min_cols, max_cols) in column_count_patterns.items():
            if min_cols <= len(columns) <= max_cols:
                pattern_score += 0.1
        
        # Data pattern analysis (if we have sample data)
        if not df.empty and len(df) > 0:
            pattern_score += self._analyze_data_patterns(df, mapping)
        
        return min(pattern_score, 1.0)
    
    def _analyze_data_patterns(self, df: pd.DataFrame, mapping: Dict) -> float:
        """Analyze actual data patterns for exchange identification."""
        score = 0.0
        
        try:
            # Look for exchange-specific data patterns
            for col in df.columns:
                col_lower = col.lower()
                
                # Check for specific data formats
                if 'time' in col_lower or 'date' in col_lower:
                    sample_values = df[col].dropna().head(3)
                    for val in sample_values:
                        val_str = str(val).lower()
                        # ISO format (common in APIs)
                        if 't' in val_str and ('z' in val_str or '+' in val_str):
                            score += 0.1
                        # Unix timestamp
                        elif val_str.isdigit() and len(val_str) >= 10:
                            score += 0.1
                
                # Check for trading pair formats
                if 'pair' in col_lower or 'market' in col_lower or 'symbol' in col_lower:
                    sample_values = df[col].dropna().head(3)
                    for val in sample_values:
                        val_str = str(val).upper()
                        # Kraken format (XBTUSD, XETHZUSD)
                        if val_str.startswith('X') and len(val_str) >= 6:
                            score += 0.2
                        # Standard pair format (BTC/USD, BTCUSDT)
                        elif any(sep in val_str for sep in ['/', '-', 'USD', 'BTC', 'ETH']):
                            score += 0.1
                
                # Check for transaction types
                if 'type' in col_lower or 'side' in col_lower:
                    sample_values = df[col].dropna().head(5)
                    unique_types = set(str(val).lower() for val in sample_values)
                    
                    # Common exchange types
                    common_types = {'buy', 'sell', 'deposit', 'withdraw', 'trade'}
                    if len(unique_types & common_types) >= 2:
                        score += 0.2
        
        except Exception as e:
            logger.debug(f"Error in data pattern analysis: {e}")
        
        return score
    
    def _check_exchange_patterns(self, columns: List[str], df: pd.DataFrame, mapping: Dict) -> float:
        """Check for exchange-specific patterns in data."""
        pattern_score = 0.0
        
        # Binance patterns
        if any('binance' in col for col in columns):
            pattern_score += 0.5
        
        # Coinbase patterns
        if 'spot price currency' in ' '.join(columns):
            pattern_score += 0.4
        
        # Kraken patterns (X/Z prefixes in pairs)
        if any(col.startswith('x') or col.startswith('z') for col in columns):
            pattern_score += 0.3
        
        # Check data patterns if we have sample data
        if not df.empty:
            # Look for common transaction types
            type_columns = [col for col in df.columns if 'type' in col.lower()]
            if type_columns:
                type_col = type_columns[0]
                unique_types = df[type_col].str.lower().unique()
                
                # Binance-style types
                if any(t in ['buy', 'sell', 'deposit', 'withdraw'] for t in unique_types if pd.notna(t)):
                    pattern_score += 0.2
                
                # Coinbase-style types
                if any(t in ['buy', 'sell', 'receive', 'send'] for t in unique_types if pd.notna(t)):
                    pattern_score += 0.2
        
        return min(pattern_score, 1.0)  # Cap at 1.0
    
    def scan_input_folder(self, input_dir: str = "input") -> List[Dict]:
        """
        Scan input folder for CSV/XLSX files and detect their formats.
        
        Args:
            input_dir: Directory to scan for files
            
        Returns:
            List of detection results for each file
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            logger.warning(f"Input directory {input_dir} does not exist")
            return []
        
        results = []
        supported_extensions = ['.csv', '.xlsx']
        
        for file_path in input_path.iterdir():
            if file_path.suffix.lower() in supported_extensions:
                logger.info(f"Analyzing {file_path.name}...")
                
                exchange, confidence, details = self.detect_exchange(str(file_path))
                
                result = {
                    'file_path': str(file_path),
                    'file_name': file_path.name,
                    'detected_exchange': exchange,
                    'confidence': confidence,
                    'details': details,
                    'needs_confirmation': confidence < self.confidence_threshold
                }
                
                results.append(result)
        
        return results
    
    def get_exchange_suggestions(self, columns: List[str], top_n: int = 3) -> List[Tuple[str, float]]:
        """
        Get top N exchange suggestions based on column analysis.
        
        Args:
            columns: List of column names from the file
            top_n: Number of top suggestions to return
            
        Returns:
            List of (exchange_name, confidence_score) tuples
        """
        scores = {}
        for exchange, mapping in self.exchange_mappings.items():
            score, _ = self._calculate_match_score(columns, mapping, pd.DataFrame())
            scores[exchange] = score
        sorted_exchanges = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_exchanges[:top_n]


def auto_process_input_folder(input_dir: str = "input", 
                            output_dir: str = "output",
                            interactive: bool = True,
                            ml_fallback: bool = False) -> List[Dict]:
    """
    Automatically process all files in input folder with exchange detection.
    
    Args:
        input_dir: Directory containing input files
        output_dir: Directory for output files
        interactive: Whether to ask for user confirmation
        ml_fallback: Whether to use ML mapping when detection is low confidence or unknown
        
    Returns:
        List of processing results
    """
    detector = ExchangeDetector()
    results = []
    
    # Scan input folder
    detections = detector.scan_input_folder(input_dir)
    
    if not detections:
        print(f"No CSV or XLSX files found in {input_dir} directory")
        return results
    
    print(f"\nFound {len(detections)} files to process:\n")
    
    for detection in detections:
        file_name = detection['file_name']
        detected_exchange = detection['detected_exchange']
        confidence = detection['confidence']
        
        print(f"File: {file_name}")
        print(f"   Detected Exchange: {detected_exchange}")
        print(f"   Confidence: {confidence:.1%}")
        
        # Determine if we need user confirmation
        confirmed_exchange = detected_exchange
        
        if ml_fallback and (detection['needs_confirmation'] or detected_exchange == 'unknown'):
            confirmed_exchange = 'ml'
            print(f"   Using ML fallback mapping")
        elif interactive and (detection['needs_confirmation'] or detected_exchange == 'unknown'):
            print(f"   Low confidence detection")
            
            # Show top suggestions
            columns = detection['details'].get('columns_found', [])
            if columns:
                suggestions = detector.get_exchange_suggestions(columns, 3)
                print(f"   Suggestions:")
                for i, (exchange, score) in enumerate(suggestions, 1):
                    print(f"      {i}. {exchange} ({score:.1%})")
            
            # Ask user for confirmation
            user_input = input(f"   Confirm exchange (press Enter for '{detected_exchange}' or type correct exchange): ").strip()
            
            if user_input:
                if user_input.lower() in detector.exchange_mappings:
                    confirmed_exchange = user_input.lower()
                    print(f"   Using: {confirmed_exchange}")
                else:
                    print(f"   Unknown exchange '{user_input}'. Using detected: {detected_exchange}")
            else:
                print(f"   Using detected: {detected_exchange}")
        
        # Process the file
        try:
            from normalize import normalize_csv
            
            # Generate output filename
            base_name = Path(file_name).stem
            output_file = os.path.join(output_dir, f"{base_name}_normalized.csv")
            
            print(f"   Processing with {confirmed_exchange} format...")
            
            normalize_csv(
                input_file=detection['file_path'],
                exchange=confirmed_exchange,
                output_file=output_file,
                fetch_missing_prices=True,
                remove_duplicates=True
            )
            
            result = {
                'input_file': detection['file_path'],
                'output_file': output_file,
                'exchange_used': confirmed_exchange,
                'detection_confidence': confidence,
                'status': 'success'
            }
            
            print(f"   Normalized to: {output_file}")
            
        except Exception as e:
            result = {
                'input_file': detection['file_path'],
                'exchange_used': confirmed_exchange,
                'detection_confidence': confidence,
                'status': 'error',
                'error': str(e)
            }
            
            print(f"   Error: {e}")
        
        results.append(result)
        print()  # Empty line for readability
    
    return results


def interactive_exchange_selection(file_path: str) -> str:
    """
    Interactive exchange selection for a specific file.
    
    Args:
        file_path: Path to the file to analyze
        
    Returns:
        Selected exchange name
    """
    detector = ExchangeDetector()
    
    # Detect exchange
    exchange, confidence, details = detector.detect_exchange(file_path)
    
    print(f"\nAnalyzing: {Path(file_path).name}")
    print(f"Detected Exchange: {exchange} (confidence: {confidence:.1%})")
    
    if confidence < detector.confidence_threshold:
        print("Low confidence detection")
        
        # Show column analysis
        if 'columns_found' in details:
            print(f"Columns found: {', '.join(details['columns_found'])}")
        
        # Show suggestions
        columns = details.get('columns_found', [])
        if columns:
            suggestions = detector.get_exchange_suggestions(columns, 5)
            print("\nTop suggestions:")
            for i, (exch, score) in enumerate(suggestions, 1):
                print(f"   {i}. {exch} ({score:.1%})")
        
        # Get user input
        print(f"\nOptions:")
        print(f"   1. Use detected exchange: {exchange}")
        print(f"   2. Enter different exchange name")
        print(f"   3. Show all supported exchanges")
        
        choice = input("Enter choice (1-3) or exchange name: ").strip()
        
        if choice == '1' or choice == '':
            return exchange
        elif choice == '2':
            new_exchange = input("Enter exchange name: ").strip().lower()
            if new_exchange in detector.exchange_mappings:
                return new_exchange
            else:
                print(f"Unknown exchange: {new_exchange}")
                return exchange
        elif choice == '3':
            print("\nAll supported exchanges:")
            for i, exch in enumerate(sorted(detector.exchange_mappings.keys()), 1):
                print(f"   {i:2d}. {exch}")
            
            selected = input("\nEnter exchange name: ").strip().lower()
            if selected in detector.exchange_mappings:
                return selected
            else:
                print(f"Unknown exchange: {selected}")
                return exchange
        else:
            # Try to use the input as exchange name
            if choice.lower() in detector.exchange_mappings:
                return choice.lower()
            else:
                print(f"Unknown option: {choice}")
                return exchange
    
    return exchange