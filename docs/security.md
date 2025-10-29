# Security Policy

##  Privacy and Security

The Crypto Tax Tool is designed with privacy and security as core principles.

##  Security Features

### Local Processing Only
- **All transaction data** remains on your local machine
- **No data transmission** of sensitive financial information
- **No cloud storage** or external data processing
- **No user accounts** or authentication required

### Data Protection
- **Temporary files** use appropriate file permissions
- **Memory management** clears sensitive data after processing
- **No persistent storage** of transaction details beyond user-specified outputs
- **Secure file handling** with proper error handling and cleanup

### API Security
- **HTTPS only** for all external API calls
- **Public data only** - only cryptocurrency prices are fetched, never transaction details
- **Rate limiting** respects API provider terms of service
- **No API keys** stored or transmitted for price data

##  What Data is Processed Locally

### Input Data (Stays Local)
- Transaction history from exchanges
- Wallet addresses and balances
- Trading amounts and dates
- Personal financial information

### External API Calls (Public Data Only)
- Cryptocurrency price data from CoinGecko
- Historical price information (asset symbol + date only)
- No personal or transaction-specific data transmitted

##  Reporting Security Issues

If you discover a security vulnerability, please report it responsibly:

### Contact Information
- **Email**: [Create a GitHub issue with "Security" label]
- **Response Time**: We aim to respond within 48 hours
- **Disclosure**: Please allow reasonable time for fixes before public disclosure

### What to Include
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fixes (if any)

##  Security Best Practices for Users

### File Handling
- **Keep backups** of original exchange export files
- **Use secure storage** for sensitive financial data
- **Delete temporary files** after processing if desired
- **Verify file integrity** before processing

### System Security
- **Keep software updated** (Python, dependencies)
- **Use antivirus software** on your system
- **Secure your computer** with appropriate access controls
- **Use encrypted storage** for sensitive financial documents

### Data Verification
- **Review all outputs** before using for tax purposes
- **Cross-check calculations** with exchange records
- **Validate price data** against known market prices
- **Consult tax professionals** for complex situations

##  Technical Security Measures

### Input Validation
- **File type validation** prevents malicious file processing
- **Size limits** prevent resource exhaustion attacks
- **Data sanitization** prevents injection attacks
- **Error handling** prevents information disclosure

### Dependency Security
- **Minimal dependencies** reduce attack surface
- **Well-maintained libraries** with active security updates
- **No network dependencies** for core functionality
- **Open source libraries** with community security review

### Code Security
- **No eval() or exec()** functions used
- **Safe file operations** with proper path validation
- **Memory-safe operations** with appropriate bounds checking
- **Error handling** prevents crashes and data leaks

##  Security Checklist for Contributors

When contributing code, ensure:

- [ ] No hardcoded credentials or API keys
- [ ] Proper input validation for all user inputs
- [ ] Safe file operations with path validation
- [ ] No execution of user-provided code
- [ ] Appropriate error handling without information disclosure
- [ ] No logging of sensitive data
- [ ] Secure handling of temporary files
- [ ] No network calls with user data

##  Security Updates

### Update Policy
- **Critical security issues**: Immediate patch release
- **High severity issues**: Patch within 7 days
- **Medium severity issues**: Patch in next minor release
- **Low severity issues**: Patch in next major release

### Notification Process
- Security updates will be clearly marked in release notes
- Critical updates will be announced prominently
- Users are encouraged to update promptly

##  Additional Resources

### Privacy Resources
- [Privacy Policy](privacy.md) - Detailed privacy practices
- [Data Handling](data-handling.md) - How data is processed
- [FAQ Security Section](faq.md#security) - Common security questions

### Security Tools
- Use file integrity checkers for important data
- Consider encrypted storage for sensitive files
- Regular system security updates
- Backup strategies for financial data

##  Legal and Compliance

### Disclaimer
- This tool is provided "as-is" without security warranties
- Users are responsible for their own data security
- No liability for data breaches or security issues
- Users should follow local data protection laws

### Compliance
- Tool designed to comply with general data protection principles
- No collection of personal data by the application
- Users responsible for compliance with local regulations
- Consult legal professionals for specific compliance requirements

---

**Remember**: The best security practice is to keep your financial data secure and only use trusted, open-source tools like this one for processing sensitive information.