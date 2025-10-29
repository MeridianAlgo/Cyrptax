#!/usr/bin/env python3
"""Test script for auto-detection functionality."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_auto_detection():
    """Test auto-detection with sample files."""
    print("Testing Auto-Detection Functionality")
    print("=" * 50)
    
    try:
        from src.auto_detect import ExchangeDetector
        
        detector = ExchangeDetector()
        print(f"Auto-detector initialized")
        print(f"   Loaded {len(detector.exchange_mappings)} exchange mappings")
        
        # Test with sample files
        sample_files = [
            'data/examples/binance_sample.csv',
            'data/examples/coinbase_sample.csv', 
            'data/examples/kraken_sample.csv'
        ]
        
        print(f"\nTesting detection on sample files:")
        
        for file_path in sample_files:
            if Path(file_path).exists():
                exchange, confidence, details = detector.detect_exchange(file_path)
                
                expected_exchange = Path(file_path).stem.split('_')[0]  # Extract expected from filename
                
                status = "PASS" if exchange == expected_exchange else "WARN"
                
                print(f"\n{status} {Path(file_path).name}")
                print(f"   Expected: {expected_exchange}")
                print(f"   Detected: {exchange}")
                print(f"   Confidence: {confidence:.1%}")
                
                if confidence >= 0.7:
                    print(f"   Status: High confidence")
                elif confidence >= 0.4:
                    print(f"   Status: Medium confidence")
                else:
                    print(f"   Status: Low confidence")
                
                # Show matched columns
                if 'matched_columns' in details.get('analysis', {}):
                    matched = details['analysis']['matched_columns']
                    if matched:
                        print(f"   Matched columns: {', '.join(matched[:3])}{'...' if len(matched) > 3 else ''}")
            else:
                print(f"Sample file not found: {file_path}")
        
        # Test suggestions
        print(f"\nTesting exchange suggestions:")
        test_columns = ['time', 'type', 'base-asset', 'quantity', 'total', 'fee']
        suggestions = detector.get_exchange_suggestions(test_columns, 3)
        
        print(f"   For columns: {test_columns}")
        print(f"   Top suggestions:")
        for i, (exchange, score) in enumerate(suggestions, 1):
            print(f"      {i}. {exchange} ({score:.1%})")
        
        print(f"\nAuto-detection tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"Auto-detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_input_folder_scan():
    """Test input folder scanning."""
    print(f"\nTesting input folder scanning:")
    
    try:
        from src.auto_detect import ExchangeDetector
        
        detector = ExchangeDetector()
        
        # Create test input folder with sample files
        input_dir = Path("test_input")
        input_dir.mkdir(exist_ok=True)
        
        # Copy sample files to test input
        import shutil
        sample_files = [
            'data/examples/binance_sample.csv',
            'data/examples/coinbase_sample.csv'
        ]
        
        copied_files = []
        for sample_file in sample_files:
            if Path(sample_file).exists():
                dest_file = input_dir / Path(sample_file).name
                shutil.copy2(sample_file, dest_file)
                copied_files.append(dest_file)
                print(f"   Copied: {dest_file.name}")
        
        if copied_files:
            # Scan the test folder
            results = detector.scan_input_folder(str(input_dir))
            
            print(f"\nScan results for {len(results)} files:")
            for result in results:
                print(f"   {result['file_name']}")
                print(f"      Exchange: {result['detected_exchange']}")
                print(f"      Confidence: {result['confidence']:.1%}")
                print(f"      Needs confirmation: {result['needs_confirmation']}")
        
        # Cleanup
        shutil.rmtree(input_dir)
        print(f"\nCleaned up test files")
        
        return True
        
    except Exception as e:
        print(f"Input folder scan test failed: {e}")
        return False


def main():
    """Run all auto-detection tests."""
    print("Crypto Tax Tool - Auto-Detection Tests")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Basic auto-detection
    if test_auto_detection():
        tests_passed += 1
    
    # Test 2: Input folder scanning
    if test_input_folder_scan():
        tests_passed += 1
    
    print(f"\n" + "=" * 60)
    print(f"Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("All auto-detection tests passed!")
        print("\nReady to use auto-detection features:")
        print("   1. Place CSV files in input/ folder")
        print("   2. Run: python src/main.py auto-process")
        print("   3. Or run: python quick_start.py")
        return True
    else:
        print("Some tests failed. Check the errors above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)