# Contributing to Crypto Tax Tool

Thank you for your interest in contributing to the Crypto Tax Tool! This document provides guidelines for contributing to the project.

## Ways to Contribute

-  **Report bugs** - Help us identify and fix issues
-  **Suggest features** - Propose new functionality or improvements
-  **Submit code** - Fix bugs, add features, or improve documentation
-  **Improve documentation** - Help make the project more accessible
-  **Add exchange support** - Help support more cryptocurrency exchanges

## Getting Started

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/Cryptax.git
   cd Cryptax
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install pytest pytest-cov black flake8 mypy
   ```

3. **Run tests to verify setup**
   ```bash
   python run_tests.py --quick
   ```

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run full test suite
   python run_tests.py --all
   
   # Run specific tests
   python run_tests.py --unit
   python run_tests.py --integration
   ```

4. **Submit a pull request**
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure all tests pass

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Maximum line length: 100 characters
- Use type hints where appropriate

### Code Quality

- Write clear, self-documenting code
- Add docstrings for all public functions and classes
- Include error handling and logging
- Follow existing patterns and conventions

### Testing Requirements

- Add unit tests for all new functions
- Include integration tests for new workflows
- Maintain minimum 80% code coverage
- Test both success and failure scenarios

## Adding Exchange Support

To add support for a new cryptocurrency exchange:

### 1. Create Exchange Mapping

Add the exchange configuration to `config/exchanges.yaml`:

```yaml
new_exchange:
  timestamp: "Date"
  type: "Type" 
  base_asset: "Asset"
  base_amount: "Amount"
  quote_asset: "Currency"
  quote_amount: "Total"
  fee_amount: "Fee"
  fee_asset: "Fee Currency"
  notes: "Notes"
  
  # Optional: Unique identifiers for better detection
  unique_columns:
    - "Exchange Specific Column"
  
  # Optional: Signature patterns for detection
  signature_patterns:
    - "unique_pattern_in_headers"
```

### 2. Add Sample Data

Create a sample file in `data/examples/new_exchange_sample.csv` with:
- Representative transaction data (anonymized)
- All supported transaction types
- Various assets and currencies

### 3. Add Tests

Create tests in `tests/test_normalize.py`:

```python
def test_normalize_new_exchange_format(self):
    """Test normalization of New Exchange format CSV."""
    # Add comprehensive test cases
```

### 4. Update Documentation

- Add exchange to supported list in README.md
- Document any special requirements in `docs/input_formats.md`
- Update exchange count in documentation

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Environment details** (OS, Python version)
- **Sample data** (anonymized) if relevant
- **Error messages** and stack traces

### Feature Requests

For feature requests, please provide:

- **Clear description** of the proposed feature
- **Use case** and motivation
- **Proposed implementation** (if you have ideas)
- **Potential impact** on existing functionality

## Code Review Process

1. **Automated checks** must pass (tests, linting, coverage)
2. **Manual review** by maintainers
3. **Discussion** and feedback incorporation
4. **Approval** and merge

### Review Criteria

- Code quality and style compliance
- Test coverage and quality
- Documentation completeness
- Backward compatibility
- Security considerations

## Documentation Guidelines

### Code Documentation

- Use clear, descriptive docstrings
- Include parameter and return type information
- Provide usage examples for complex functions
- Document any side effects or assumptions

### User Documentation

- Write for users with varying technical expertise
- Include practical examples and use cases
- Keep documentation up-to-date with code changes
- Use clear, concise language

## Security Considerations

### Privacy Protection

- Never commit real transaction data
- Anonymize all sample data
- Protect user privacy in error messages
- Follow data minimization principles

### Code Security

- Validate all user inputs
- Handle errors gracefully
- Avoid hardcoded secrets or credentials
- Follow secure coding practices

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Maintain a welcoming environment

### Communication

- Use clear, professional language
- Be patient with questions and feedback
- Provide helpful, actionable suggestions
- Acknowledge contributions and help

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, backward compatible

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version number bumped
- [ ] Release notes prepared

## Getting Help

### Resources

- **Documentation**: Check the `docs/` directory
- **FAQ**: See `docs/faq.md` for common questions
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions for questions

### Contact

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: For security issues or private matters

## Recognition

Contributors are recognized in:
- `docs/credits.md` - All contributors
- Release notes - Major contributions
- GitHub contributors page - Automatic recognition

Thank you for contributing to the Crypto Tax Tool! Your help makes this project better for everyone in the cryptocurrency community.