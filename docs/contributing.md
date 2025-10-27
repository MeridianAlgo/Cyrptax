# Contributing to Crypto Tax Tool

Thank you for your interest in contributing to the Crypto Tax Tool! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use the issue template** when creating new issues
3. **Provide detailed information**:
   - Operating system and Python version
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Sample data (anonymized) if relevant
   - Error messages and stack traces

### Suggesting Features

1. **Check existing feature requests** to avoid duplicates
2. **Describe the use case** and why the feature would be valuable
3. **Provide implementation ideas** if you have them
4. **Consider backward compatibility** and impact on existing users

### Code Contributions

#### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/crypto-tax-tool.git
   cd crypto-tax-tool
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If it exists
   ```

#### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** following the coding standards below
3. **Write or update tests** for your changes
4. **Update documentation** if needed
5. **Test your changes** thoroughly

#### Coding Standards

- **Follow PEP 8** Python style guidelines
- **Use type hints** where appropriate
- **Write docstrings** for all functions and classes
- **Keep functions focused** and reasonably sized
- **Use meaningful variable names**
- **Add comments** for complex logic

#### Example Code Style

```python
def calculate_gain_loss(proceeds: float, cost_basis: float, 
                       holding_period_days: int) -> Dict[str, Any]:
    """
    Calculate capital gain/loss for a transaction.
    
    Args:
        proceeds: Sale proceeds in base currency
        cost_basis: Original cost basis
        holding_period_days: Number of days held
        
    Returns:
        Dictionary with gain/loss details
    """
    gain_loss = proceeds - cost_basis
    is_short_term = holding_period_days < 365
    
    return {
        'gain_loss': gain_loss,
        'short_term': is_short_term,
        'proceeds': proceeds,
        'cost_basis': cost_basis
    }
```

#### Testing

- **Write unit tests** for new functionality
- **Update existing tests** when modifying code
- **Ensure all tests pass** before submitting
- **Aim for good test coverage** (80%+ is ideal)

Run tests with:
```bash
python -m pytest tests/
```

#### Submitting Changes

1. **Commit your changes** with clear messages:
   ```bash
   git add .
   git commit -m "Add support for new exchange XYZ"
   ```
2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
3. **Create a pull request** on GitHub
4. **Fill out the PR template** completely
5. **Respond to review feedback** promptly

## 📋 Specific Contribution Areas

### Adding Exchange Support

The most common contribution is adding support for new exchanges:

1. **Analyze the exchange's CSV format**
2. **Add mapping to `config/exchanges.yaml`**:
   ```yaml
   new_exchange:
     timestamp: Date
     type: Transaction Type
     base_asset: Asset
     base_amount: Amount
     quote_asset: Currency
     quote_amount: Total
     fee_amount: Fee
     fee_asset: Fee Currency
     notes: Notes
   ```
3. **Create sample data** in `data/examples/`
4. **Test the normalization** process
5. **Update documentation** to list the new exchange

### Improving Tax Calculations

- **Add new accounting methods** (e.g., specific identification)
- **Improve handling of edge cases** (forks, airdrops, etc.)
- **Add support for different jurisdictions**
- **Optimize performance** for large datasets

### Enhancing Reports

- **Add new report formats** (e.g., other tax software)
- **Improve existing report layouts**
- **Add data visualizations**
- **Support multiple currencies**

### Documentation Improvements

- **Fix typos and grammar**
- **Add more examples**
- **Improve API documentation**
- **Create video tutorials**

## 🔧 Development Setup

### Prerequisites

- Python 3.7+
- Git
- Text editor or IDE

### Development Dependencies

Install additional development tools:
```bash
pip install pytest pytest-cov flake8 black mypy
```

### Code Quality Tools

- **Linting**: `flake8 src/`
- **Formatting**: `black src/`
- **Type checking**: `mypy src/`
- **Testing**: `pytest tests/ --cov=src`

### Project Structure

```
crypto-tax-tool/
├── src/                    # Main source code
│   ├── __init__.py
│   ├── main.py            # CLI entry point
│   ├── normalize.py       # Data normalization
│   ├── calculate.py       # Tax calculations
│   ├── report.py          # Report generation
│   ├── validate.py        # Data validation
│   ├── price_fetch.py     # Price fetching
│   └── config.py          # Configuration management
├── config/                # Configuration files
│   ├── exchanges.yaml     # Exchange mappings
│   └── app.conf          # Application settings
├── tests/                 # Test suite
├── docs/                  # Documentation
├── data/examples/         # Sample data
└── output/               # Generated files
```

## 📝 Pull Request Guidelines

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts with main branch

### PR Description Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing performed
- [ ] All tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## 🐛 Bug Reports

### Information to Include

1. **Environment details**:
   - Operating system
   - Python version
   - Package versions (`pip freeze`)

2. **Steps to reproduce**:
   - Exact commands run
   - Input files used (anonymized)
   - Configuration settings

3. **Expected behavior**
4. **Actual behavior**
5. **Error messages** (full stack trace)
6. **Additional context**

### Sample Bug Report

```markdown
**Environment:**
- OS: Windows 10
- Python: 3.9.7
- Tool version: 0.2.0

**Steps to reproduce:**
1. Run `python src/main.py normalize data.csv binance`
2. File contains 1000+ transactions

**Expected:** Normalization completes successfully
**Actual:** Process crashes with memory error

**Error message:**
```
MemoryError: Unable to allocate 2.5 GiB for an array
```

**Additional context:**
File size is 50MB with many duplicate transactions.
```

## 🎯 Feature Requests

### Information to Include

1. **Use case description**
2. **Current workaround** (if any)
3. **Proposed solution**
4. **Alternative solutions** considered
5. **Impact on existing functionality**

## 📚 Documentation Standards

### Code Documentation

- **Module docstrings** at the top of each file
- **Function docstrings** using Google style:
  ```python
  def function_name(param1: type, param2: type) -> return_type:
      """
      Brief description of function.
      
      Args:
          param1: Description of param1
          param2: Description of param2
          
      Returns:
          Description of return value
          
      Raises:
          ExceptionType: Description of when this exception is raised
      """
  ```
- **Inline comments** for complex logic
- **Type hints** for function parameters and returns

### User Documentation

- **Clear examples** with expected output
- **Step-by-step instructions**
- **Troubleshooting sections**
- **Screenshots** where helpful

## 🏆 Recognition

Contributors will be recognized in:
- **README.md** acknowledgments section
- **CHANGELOG.md** for significant contributions
- **GitHub contributors** page

## 📞 Getting Help

- **GitHub Discussions** for questions and ideas
- **GitHub Issues** for bugs and feature requests
- **Email** maintainers for security issues

## 📄 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to the Crypto Tax Tool! 🚀