---
name: Exchange Support Request
about: Request support for a new cryptocurrency exchange
title: '[EXCHANGE] Add support for [Exchange Name]'
labels: 'exchange-support'
assignees: ''

---

**Exchange Information**
- **Exchange Name**: [e.g. NewExchange]
- **Exchange Website**: [e.g. https://newexchange.com]
- **Exchange Type**: [e.g. Centralized Exchange, DEX, Wallet]

**Export Format**
- **File Format**: [e.g. CSV, XLSX, JSON]
- **Export Location**: [Describe where users can find the export feature]
- **Export Instructions**: [Brief steps to export transaction data]

**Sample Data Structure**
Please provide a sample of the CSV/XLSX structure (with anonymized data):

```csv
Date,Type,Asset,Amount,Price,Fee,Total
2024-01-01,Buy,BTC,0.1,50000,25,5025
2024-01-02,Sell,BTC,0.05,51000,12.75,2537.25
```

**Column Mapping**
Help us understand what each column represents:
- Date: Transaction timestamp
- Type: Transaction type (buy/sell/deposit/withdraw)
- Asset: Cryptocurrency symbol
- Amount: Quantity of cryptocurrency
- Price: Price per unit
- Fee: Transaction fee
- Total: Total amount in fiat currency

**Transaction Types**
What transaction types does this exchange support in exports?
- [ ] Buy/Sell
- [ ] Deposit/Withdraw
- [ ] Staking rewards
- [ ] Airdrops
- [ ] Trading fees
- [ ] Other: [specify]

**Special Considerations**
Are there any special formatting or parsing considerations for this exchange?
- Date format: [e.g. YYYY-MM-DD HH:MM:SS]
- Decimal separator: [e.g. . or ,]
- Currency symbols: [e.g. BTC, Bitcoin, etc.]
- Multiple sheets in XLSX: [Yes/No]

**Sample File (Optional)**
If you can provide an anonymized sample file, please attach it. Make sure to:
- Remove all personal information
- Replace real amounts with representative values
- Keep the original structure and formatting

**Priority**
How popular/important is this exchange?
- [ ] Major exchange (high volume, many users)
- [ ] Regional exchange (popular in specific region)
- [ ] Specialized exchange (DeFi, specific features)
- [ ] Personal request (low priority)

**Additional Information**
Any other information that might help with implementation.