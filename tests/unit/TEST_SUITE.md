# Comprehensive Test Suite Documentation

This document describes the comprehensive test suite for the Crypto Tax Tool, including test organization, execution, and coverage requirements.

## Test Suite Overview

The test suite is designed to ensure the reliability, accuracy, and performance of the crypto tax calculation tool. It covers all major components and workflows with different types of tests.

### Test Categories

#### 1. Unit Tests
- **Purpose**: Test individual functions and classes in isolation
- **Coverage**: All core modules (normalize, calculate, validate, report, price_fetch, auto_detect)
- **Location**: `tests/test_*.py`
- **Execution Time**: < 30 seconds
- **Coverage Target**: 90%+

#### 2. Integration Tests
- **Purpose**: Test component interactions and workflows
- **Coverage**: CLI interface, end-to-end workflows, module integration
- **Location**: `tests/test_cli.py`, workflow tests in other files
- **Execution Time**: < 2 minutes
- **Coverage Target**: 85%+

#### 3. Performance Tests
- **Purpose**: Ensure acceptable performance with large datasets
- **Coverage**: Large file processing, memory usage, calculation speed
- **Location**: Performance test methods marked with `@pytest.mark.performance`
- **Execution Time**: < 5 minutes
- **Thresholds**: See performance requirements below

#### 4. Network Tests
- **Purpose**: Test external API integrations
- **Coverage**: CoinGecko API, price fetching, error handling
- **Location**: Tests marked with `@pytest.mark.network`
- **Execution Time**: Variable (depends on network)
- **Note**: Skipped by default, run with `--network` flag

## Test Files Structure

```
tests/
 conftest.py              # Pytest configuration and fixtures
 test_normalize.py        # Normalization module tests
 test_validate.py         # Validation module tests
 test_calculate.py        # Tax calculation tests
 test_price_fetch.py      # Price fetching tests
 test_report.py           # Report generation tests
 test_cli.py              # CLI interface tests
 test_auto_detect.py      # Auto-detection tests (existing)
 test_basic.py            # Basic functionality tests (existing)
 unit/                    # Additional unit tests
 integration/             # Integration test scenarios
 fixtures/                # Test data and mock responses
 TEST_SUITE.md           # This documentation
```

## Test Execution

### Quick Test Suite (Default)
```bash
python run_tests.py
# or
python run_tests.py --quick
```

Includes:
- Smoke tests
- Unit tests (excluding slow tests)
- Basic integration tests
- Project structure validation

### Comprehensive Test Suite
```bash
python run_tests.py --all
```

Includes all test categories plus:
- Performance tests
- Network tests (if available)
- Code quality checks
- Security analysis

### Specific Test Categories
```bash
# Unit tests only
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration

# Performance tests only
python run_tests.py --performance

# Network tests only
python run_tests.py --network
```

### Coverage Analysis
```bash
python run_tests.py --coverage
```

Generates:
- HTML coverage report (`htmlcov/index.html`)
- XML coverage report (`coverage.xml`)
- Terminal coverage summary

### CI/CD Pipeline Tests
```bash
python run_tests.py --ci
```

Optimized for continuous integration:
- All critical tests
- Coverage analysis
- Code quality checks
- Test reports in CI-friendly formats

## Test Data and Fixtures

### Sample Data Files
- `sample_binance_csv`: Binance format transaction data
- `sample_coinbase_csv`: Coinbase format transaction data
- `sample_kraken_csv`: Kraken format transaction data
- `sample_normalized_csv`: Normalized transaction data
- `sample_gains_dataframe`: Tax calculation results
- `sample_income_data`: Income events (staking, airdrops)

### Mock Data
- `mock_price_data`: Historical price data for testing
- Mock API responses for external services
- Test configuration files

### Temporary Resources
- Automatic cleanup of temporary files
- Isolated test environments
- Database fixtures for complex scenarios

## Coverage Requirements

### Overall Coverage Targets
- **Minimum**: 80% line coverage
- **Target**: 90% line coverage
- **Critical modules**: 95% coverage (calculate, normalize, validate)

### Module-Specific Requirements

#### Core Modules (95% coverage required)
- `normalize.py`: Data normalization and exchange format handling
- `calculate.py`: Tax calculations (FIFO, LIFO, HIFO)
- `validate.py`: Data validation and error detection

#### Important Modules (90% coverage required)
- `price_fetch.py`: Price fetching and caching
- `report.py`: Report generation
- `auto_detect.py`: Exchange format detection

#### Supporting Modules (85% coverage required)
- `config.py`: Configuration management
- `exceptions.py`: Error handling
- `main.py`: CLI interface

### Coverage Exclusions
- Error handling for external service failures
- Platform-specific code paths
- Debug and development utilities
- Abstract base classes and protocols

## Performance Requirements

### Processing Speed
- **Small datasets** (< 1,000 transactions): < 5 seconds
- **Medium datasets** (1,000 - 10,000 transactions): < 30 seconds
- **Large datasets** (10,000+ transactions): < 2 minutes

### Memory Usage
- **Maximum memory**: 500MB for 100,000 transactions
- **Memory growth**: Linear with dataset size
- **No memory leaks**: Stable memory usage over multiple runs

### API Performance
- **Price fetching**: < 2 seconds per request
- **Batch operations**: < 1 second per 10 requests
- **Cache hit ratio**: > 80% for repeated requests

## Test Quality Standards

### Test Design Principles
1. **Independence**: Tests don't depend on each other
2. **Repeatability**: Consistent results across runs
3. **Clarity**: Clear test names and documentation
4. **Completeness**: Cover both success and failure cases
5. **Efficiency**: Fast execution without sacrificing coverage

### Test Naming Conventions
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<functionality>_<scenario>`

Examples:
- `test_normalize_binance_format()`
- `test_calculate_fifo_multiple_lots()`
- `test_validate_missing_required_fields()`

### Assertion Guidelines
- Use specific assertions (`assert_currency_equal` for financial data)
- Include meaningful error messages
- Test both positive and negative cases
- Verify side effects and state changes

## Continuous Integration

### Pre-commit Checks
```bash
# Run before committing code
python run_tests.py --quick --lint
```

### Pull Request Validation
```bash
# Full validation for pull requests
python run_tests.py --ci
```

### Release Testing
```bash
# Comprehensive testing before release
python run_tests.py --all --coverage --report
```

## Test Maintenance

### Adding New Tests
1. Follow naming conventions
2. Use appropriate fixtures
3. Add proper markers (`@pytest.mark.unit`, etc.)
4. Update this documentation if needed

### Updating Existing Tests
1. Maintain backward compatibility
2. Update related tests when changing functionality
3. Ensure coverage doesn't decrease

### Test Data Management
1. Keep test data minimal but representative
2. Use fixtures for reusable test data
3. Clean up temporary files automatically

## Troubleshooting

### Common Issues

#### Tests Failing Locally
1. Check Python version compatibility
2. Verify all dependencies are installed
3. Ensure test data files exist
4. Check file permissions

#### Coverage Issues
1. Identify uncovered lines with `--cov-report=html`
2. Add tests for missing coverage
3. Use `# pragma: no cover` for untestable code

#### Performance Test Failures
1. Check system resources during test run
2. Adjust performance thresholds if needed
3. Profile slow tests to identify bottlenecks

#### Network Test Issues
1. Check internet connectivity
2. Verify API endpoints are accessible
3. Use mock data for unreliable external services

### Getting Help
1. Check test output for specific error messages
2. Run individual test files to isolate issues
3. Use `pytest -v -s` for detailed output
4. Review test logs in `test_results.xml`

## Test Metrics and Reporting

### Automated Reports
- **JUnit XML**: `test_results.xml` (CI integration)
- **HTML Report**: `test_report.html` (human-readable)
- **Coverage HTML**: `htmlcov/index.html` (detailed coverage)
- **Coverage XML**: `coverage.xml` (CI integration)

### Key Metrics Tracked
- Test pass/fail rates
- Code coverage percentages
- Test execution times
- Performance benchmarks
- Error rates and types

### Quality Gates
- All tests must pass
- Coverage must meet minimum thresholds
- Performance tests must meet time limits
- No critical security issues
- Code quality checks must pass

## Future Enhancements

### Planned Improvements
- [ ] Property-based testing with Hypothesis
- [ ] Mutation testing for test quality assessment
- [ ] Visual regression testing for reports
- [ ] Automated performance regression detection
- [ ] Integration with external tax software for validation

### Test Infrastructure
- [ ] Parallel test execution optimization
- [ ] Test result trending and analysis
- [ ] Automated test data generation
- [ ] Cross-platform compatibility testing
- [ ] Load testing for high-volume scenarios

This comprehensive test suite ensures the reliability and accuracy of the Crypto Tax Tool while maintaining high code quality and performance standards.