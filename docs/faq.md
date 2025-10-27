# Frequently Asked Questions (FAQ)

## 🔒 Privacy and Security

### Q: Is my financial data safe?
**A:** Yes, all processing happens locally on your computer. The tool never sends your transaction data to external servers. The only external API calls are to CoinGecko for public price data.

### Q: What data is sent to external services?
**A:** Only cryptocurrency symbols and dates are sent to CoinGecko to fetch historical prices. No transaction amounts, wallet addresses, or personal information is transmitted.

### Q: Can I use this tool offline?
**A:** Partially. You can normalize and calculate taxes offline if you don't need price fetching. For missing prices, you'll need an internet connection to access CoinGecko's API.

## 💰 Tax Calculations

### Q: Which tax method should I use?
**A:** This depends on your jurisdiction and tax strategy:
- **FIFO (First In, First Out)**: Most common, required in some jurisdictions
- **LIFO (Last In, First Out)**: May reduce gains in rising markets
- **HIFO (Highest In, First Out)**: Minimizes gains by using highest cost lots first

Consult a tax professional for advice specific to your situation.

### Q: How are staking rewards taxed?
**A:** Staking rewards are typically treated as income at fair market value when received. The tool calculates this income and also adds the rewards to your inventory with the income value as the cost basis.

### Q: What about airdrops?
**A:** Similar to staking rewards, airdrops are generally taxable income at fair market value when received. The tool handles this the same way as staking rewards.

### Q: How does the tool handle forks?
**A:** Currently, the tool doesn't have specific fork handling. You may need to manually add fork receipts as airdrop transactions with zero cost basis (consult your tax advisor).

### Q: What if I can't find the price for a transaction?
**A:** The tool will log a warning and continue processing. You can:
1. Manually research the price and add it to the CSV
2. Use a different price source
3. Consult a tax professional for guidance

## 📊 Data and Files

### Q: My exchange isn't supported. What can I do?
**A:** You can:
1. Check if there's a similar format you can convert to
2. Add the exchange mapping to `config/exchanges.yaml`
3. Submit a feature request on GitHub
4. Manually convert your data to the standard format

### Q: Can I combine data from multiple exchanges?
**A:** Yes! Normalize each exchange's data separately, then combine the normalized CSV files before running tax calculations.

### Q: What if my CSV has extra columns?
**A:** Extra columns are ignored. The tool only looks for the required columns specified in the exchange mapping.

### Q: How do I handle missing transactions?
**A:** Missing transactions can cause negative balance warnings. You should:
1. Review your exchange history for missing deposits
2. Check for transactions on other platforms
3. Add missing transactions manually to your CSV

## 🔧 Technical Issues

### Q: The tool crashes with large files. What can I do?
**A:** For large files:
1. Split the file into smaller chunks by date
2. Process each chunk separately
3. Combine the results
4. Use `--remove-duplicates` to reduce file size
5. Increase your system's available memory

### Q: I'm getting "negative balance" warnings. Is this bad?
**A:** Negative balances usually indicate:
- Missing deposit transactions
- Incorrect transaction types
- Data from before your tracking period started

Review the warnings and add missing transactions if needed.

### Q: Price fetching is very slow. Can I speed it up?
**A:** Price fetching is rate-limited to respect CoinGecko's API limits. You can:
1. Use cached prices (enabled by default)
2. Pre-populate prices in your CSV to avoid fetching
3. Process smaller batches of transactions

### Q: I'm getting import errors when running the tool.
**A:** Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

If you're still having issues, try creating a fresh virtual environment.

## 📈 Reports and Output

### Q: Can I import the TurboTax CSV directly?
**A:** The TurboTax CSV is formatted for import, but you should review it before importing. Different versions of TurboTax may have slightly different requirements.

### Q: The PDF report isn't generating. What's wrong?
**A:** PDF generation requires the `fpdf2` library. Install it with:
```bash
pip install fpdf2
```

### Q: Can I customize the reports?
**A:** Currently, reports have fixed formats. You can modify the source code in `src/report.py` or use the detailed CSV export and create custom reports in Excel/Google Sheets.

### Q: How do I handle multiple currencies?
**A:** The tool converts everything to your chosen tax currency (default: USD). Make sure to set the correct currency with `--currency` when calculating taxes.

## 🌍 International Usage

### Q: Can I use this tool outside the US?
**A:** Yes, but be aware that:
- Tax rules vary by country
- The tool uses US tax concepts (short-term vs long-term)
- You may need to adapt the reports for your local tax authority
- Consult a local tax professional

### Q: Can I use currencies other than USD?
**A:** Yes, use the `--currency` option when calculating taxes. However, price data availability may vary for non-USD currencies.

### Q: How do I handle different fiscal years?
**A:** Filter your transaction data to match your tax year before processing. The tool doesn't automatically handle fiscal year boundaries.

## 🛠️ Troubleshooting

### Q: The normalization failed with "unsupported exchange" error.
**A:** Check the spelling of the exchange name and use:
```bash
python src/main.py list-exchanges
```
to see supported exchanges.

### Q: I'm getting "file not found" errors.
**A:** Make sure:
1. The file path is correct
2. You're running the command from the right directory
3. The file exists and is readable

### Q: Validation shows many warnings. Should I be concerned?
**A:** Warnings are informational and don't stop processing. Review them to ensure data quality, but they don't necessarily indicate errors.

### Q: The calculated gains seem wrong.
**A:** Double-check:
1. All transactions are included
2. The correct tax method is used
3. Prices are accurate
4. Transaction types are correct

## 📚 Best Practices

### Q: How should I organize my crypto tax records?
**A:** Recommended approach:
1. Export data from all exchanges annually
2. Keep original export files as backups
3. Document any manual adjustments
4. Save all generated reports
5. Keep records for at least 7 years

### Q: Should I validate my results?
**A:** Yes! Always:
1. Review validation warnings
2. Spot-check calculations manually
3. Compare with exchange records
4. Have a tax professional review complex situations

### Q: How often should I run tax calculations?
**A:** For tax purposes, annually. For tracking, you might run it quarterly or monthly to stay on top of your tax situation.

## 🆘 Getting Help

### Q: Where can I get more help?
**A:** 
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and community help
- **Documentation**: Check all files in the `docs/` directory
- **Tax Professional**: For tax-specific advice

### Q: How do I report a bug?
**A:** Create a GitHub issue with:
- Your operating system and Python version
- Steps to reproduce the problem
- Error messages (full stack trace)
- Sample data (anonymized) if relevant

### Q: Can I contribute to the project?
**A:** Absolutely! See [CONTRIBUTING.md](contributing.md) for guidelines on how to contribute code, documentation, or exchange support.

## ⚖️ Legal and Compliance

### Q: Is this tool IRS-approved?
**A:** This is an independent tool, not officially endorsed by any tax authority. Always verify calculations and consult tax professionals for official guidance.

### Q: What if I find errors in my tax calculations?
**A:** If you discover errors:
1. Verify the source data is correct
2. Check if it's a tool bug or data issue
3. Consult a tax professional about amendments if needed
4. Report bugs to help improve the tool

### Q: Can I rely on this tool for my tax filing?
**A:** The tool is designed to be accurate, but you should:
- Verify calculations independently
- Have complex situations reviewed by professionals
- Keep detailed records of your process
- Understand that you're responsible for your tax filings

---

**Didn't find your question?** Check the [GitHub Discussions](https://github.com/your-repo/discussions) or create a new issue!