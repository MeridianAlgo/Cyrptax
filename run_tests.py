#!/usr/bin/env python3
"""Comprehensive test runner for the crypto tax tool."""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    if description:
        print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"Exit code: {result.returncode}")
    print(f"Duration: {end_time - start_time:.2f} seconds")
    
    if result.stdout:
        print(f"\nSTDOUT:\n{result.stdout}")
    
    if result.stderr:
        print(f"\nSTDERR:\n{result.stderr}")
    
    return result


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    required_packages = [
        'pytest',
        'pandas',
        'requests',
        'pyyaml',
        'fpdf2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'pyyaml':
                import yaml
            elif package == 'fpdf2':
                import fpdf
            else:
                __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("All dependencies satisfied!")
    return True


def run_unit_tests(args):
    """Run unit tests."""
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '-m', 'not slow and not network'
    ]
    
    if args.coverage:
        cmd.extend(['--cov=src', '--cov-report=html', '--cov-report=term'])
    
    if args.parallel:
        cmd.extend(['-n', 'auto'])
    
    result = run_command(cmd, "Unit Tests")
    return result.returncode == 0


def run_integration_tests(args):
    """Run integration tests."""
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/test_cli.py',
        'tests/test_auto_detect.py',
        '-v',
        '--tb=short',
        '-m', 'integration'
    ]
    
    if args.coverage:
        cmd.extend(['--cov=src', '--cov-append'])
    
    result = run_command(cmd, "Integration Tests")
    return result.returncode == 0


def run_performance_tests(args):
    """Run performance tests."""
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '-m', 'performance or slow'
    ]
    
    if args.benchmark:
        cmd.extend(['--benchmark-only'])
    
    result = run_command(cmd, "Performance Tests")
    return result.returncode == 0


def run_network_tests(args):
    """Run tests that require network access."""
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '-m', 'network'
    ]
    
    result = run_command(cmd, "Network Tests")
    return result.returncode == 0


def run_specific_tests(test_files):
    """Run specific test files."""
    cmd = [
        sys.executable, '-m', 'pytest',
        '-v',
        '--tb=short'
    ] + test_files
    
    result = run_command(cmd, f"Specific Tests: {', '.join(test_files)}")
    return result.returncode == 0


def run_linting():
    """Run code linting."""
    print("\nRunning code quality checks...")
    
    # Check if flake8 is available
    try:
        import flake8
        cmd = [sys.executable, '-m', 'flake8', 'src/', 'tests/', '--max-line-length=100']
        result = run_command(cmd, "Flake8 Linting")
        flake8_passed = result.returncode == 0
    except ImportError:
        print("Flake8 not installed, skipping linting")
        flake8_passed = True
    
    # Check if black is available
    try:
        import black
        cmd = [sys.executable, '-m', 'black', '--check', 'src/', 'tests/']
        result = run_command(cmd, "Black Code Formatting Check")
        black_passed = result.returncode == 0
    except ImportError:
        print("Black not installed, skipping format check")
        black_passed = True
    
    return flake8_passed and black_passed


def run_type_checking():
    """Run type checking with mypy."""
    try:
        import mypy
        cmd = [sys.executable, '-m', 'mypy', 'src/', '--ignore-missing-imports']
        result = run_command(cmd, "MyPy Type Checking")
        return result.returncode == 0
    except ImportError:
        print("MyPy not installed, skipping type checking")
        return True


def run_security_checks():
    """Run security checks."""
    try:
        import bandit
        cmd = [sys.executable, '-m', 'bandit', '-r', 'src/', '-f', 'json']
        result = run_command(cmd, "Bandit Security Check")
        return result.returncode == 0
    except ImportError:
        print("Bandit not installed, skipping security checks")
        return True


def generate_test_report():
    """Generate a comprehensive test report."""
    print("\nGenerating test report...")
    
    # Run pytest with JUnit XML output
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '--junitxml=test_results.xml',
        '--html=test_report.html',
        '--self-contained-html',
        '-v'
    ]
    
    result = run_command(cmd, "Test Report Generation")
    
    if result.returncode == 0:
        print("\nTest report generated:")
        print("  - test_results.xml (JUnit format)")
        print("  - test_report.html (HTML format)")
    
    return result.returncode == 0


def run_coverage_analysis():
    """Run detailed coverage analysis."""
    print("\nRunning coverage analysis...")
    
    # Run tests with coverage
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '--cov=src',
        '--cov-report=html',
        '--cov-report=xml',
        '--cov-report=term-missing',
        '--cov-fail-under=80'
    ]
    
    result = run_command(cmd, "Coverage Analysis")
    
    if result.returncode == 0:
        print("\nCoverage reports generated:")
        print("  - htmlcov/index.html (HTML format)")
        print("  - coverage.xml (XML format)")
    
    return result.returncode == 0


def validate_project_structure():
    """Validate project structure and required files."""
    print("\nValidating project structure...")
    
    required_files = [
        'src/main.py',
        'src/normalize.py',
        'src/calculate.py',
        'src/validate.py',
        'src/report.py',
        'src/price_fetch.py',
        'src/auto_detect.py',
        'src/config.py',
        'src/exceptions.py',
        'config/exchanges.yaml',
        'config/app.conf',
        'requirements.txt',
        'README.md',
        'LICENSE'
    ]
    
    required_dirs = [
        'src',
        'tests',
        'config',
        'input',
        'output',
        'docs'
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
        else:
            print(f"✓ {dir_path}/")
    
    if missing_files or missing_dirs:
        print(f"\nMissing files: {missing_files}")
        print(f"Missing directories: {missing_dirs}")
        return False
    
    print("Project structure validation passed!")
    return True


def run_smoke_tests():
    """Run basic smoke tests to ensure the application works."""
    print("\nRunning smoke tests...")
    
    # Test basic imports
    try:
        sys.path.insert(0, 'src')
        
        import main
        import normalize
        import calculate
        import validate
        import report
        import price_fetch
        import auto_detect
        import config
        
        print("✓ All modules import successfully")
        
        # Test CLI help
        result = subprocess.run([
            sys.executable, 'src/main.py', '--help'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ CLI help works")
        else:
            print("✗ CLI help failed")
            return False
        
        # Test list exchanges
        result = subprocess.run([
            sys.executable, 'src/main.py', 'list-exchanges'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ List exchanges works")
        else:
            print("✗ List exchanges failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Smoke test failed: {e}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Comprehensive test runner for crypto tax tool")
    
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    parser.add_argument('--integration', action='store_true', help='Run integration tests')
    parser.add_argument('--performance', action='store_true', help='Run performance tests')
    parser.add_argument('--network', action='store_true', help='Run network tests')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--lint', action='store_true', help='Run linting')
    parser.add_argument('--type-check', action='store_true', help='Run type checking')
    parser.add_argument('--security', action='store_true', help='Run security checks')
    parser.add_argument('--report', action='store_true', help='Generate test report')
    parser.add_argument('--smoke', action='store_true', help='Run smoke tests')
    parser.add_argument('--validate', action='store_true', help='Validate project structure')
    parser.add_argument('--parallel', action='store_true', help='Run tests in parallel')
    parser.add_argument('--benchmark', action='store_true', help='Run benchmarks')
    parser.add_argument('--files', nargs='+', help='Specific test files to run')
    parser.add_argument('--quick', action='store_true', help='Run quick test suite')
    parser.add_argument('--ci', action='store_true', help='Run CI test suite')
    
    args = parser.parse_args()
    
    # If no specific tests requested, run quick suite
    if not any([args.unit, args.integration, args.performance, args.network, 
                args.all, args.lint, args.type_check, args.security, 
                args.report, args.smoke, args.validate, args.files]):
        args.quick = True
    
    print("Crypto Tax Tool - Comprehensive Test Runner")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        print("\nDependency check failed. Please install missing packages.")
        return 1
    
    results = []
    
    # Validate project structure
    if args.validate or args.all or args.ci:
        results.append(("Project Structure", validate_project_structure()))
    
    # Run smoke tests
    if args.smoke or args.all or args.quick or args.ci:
        results.append(("Smoke Tests", run_smoke_tests()))
    
    # Run specific test files
    if args.files:
        results.append(("Specific Tests", run_specific_tests(args.files)))
    
    # Run unit tests
    if args.unit or args.all or args.quick or args.ci:
        results.append(("Unit Tests", run_unit_tests(args)))
    
    # Run integration tests
    if args.integration or args.all or args.ci:
        results.append(("Integration Tests", run_integration_tests(args)))
    
    # Run performance tests
    if args.performance or args.all:
        results.append(("Performance Tests", run_performance_tests(args)))
    
    # Run network tests
    if args.network or args.all:
        results.append(("Network Tests", run_network_tests(args)))
    
    # Run linting
    if args.lint or args.all or args.ci:
        results.append(("Code Linting", run_linting()))
    
    # Run type checking
    if args.type_check or args.all:
        results.append(("Type Checking", run_type_checking()))
    
    # Run security checks
    if args.security or args.all:
        results.append(("Security Checks", run_security_checks()))
    
    # Generate coverage report
    if args.coverage or args.ci:
        results.append(("Coverage Analysis", run_coverage_analysis()))
    
    # Generate test report
    if args.report or args.ci:
        results.append(("Test Report", generate_test_report()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<25} {status}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")
    
    if failed > 0:
        print(f"\n❌ {failed} test suite(s) failed")
        return 1
    else:
        print(f"\n✅ All {passed} test suite(s) passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())