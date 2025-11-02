import csv
import os
import random
from datetime import datetime, timedelta

random.seed(42)

OUTPUT_DIR = os.path.join('data', 'examples')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'binance_error_stress.csv')

HEADER = [
    'time', 'type', 'base-asset', 'quantity', 'quote-asset', 'total', 'fee', 'fee-currency'
]

ASSETS = ['BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'MATIC', 'XRP', 'DOGE', 'AVAX', 'DOT']
QUOTES = ['USDT', 'USD', 'USDC']
TYPES = [
    'buy','sell','deposit','withdraw','stake','airdrop','transfer','fee',
    'convert','reward','distribution','rebate','commission','dust','interest','loan'
]

START = datetime(2020, 1, 1)


def rnd_time(i):
    base = START + timedelta(minutes=random.randint(0, 365*24*60))
    style = random.choice(['iso','isoZ','space','slash','dayfirst','unix','unixms','excel'])
    if style == 'iso':
        return base.replace(microsecond=0).isoformat()
    if style == 'isoZ':
        return base.replace(microsecond=0).isoformat() + 'Z'
    if style == 'space':
        return base.strftime('%Y-%m-%d %H:%M:%S')
    if style == 'slash':
        return base.strftime('%Y/%m/%d %H:%M:%S')
    if style == 'dayfirst':
        return base.strftime('%d-%m-%Y %H:%M:%S')
    if style == 'unix':
        return str(int(base.timestamp()))
    if style == 'unixms':
        return str(int(base.timestamp() * 1000))
    # excel serial (days since 1899-12-30)
    excel_origin = datetime(1899, 12, 30)
    serial = (base - excel_origin).days + (base - base.replace(hour=0, minute=0, second=0, microsecond=0)).seconds/86400
    return f"{serial:.5f}"


def rnd_amount(allow_negative=False, missing_prob=0.06):
    if random.random() < missing_prob:
        return random.choice(['', 'NA', 'n/a', '-', None])
    base = random.uniform(0.00001, 5.0)
    if allow_negative and random.random() < 0.2:
        base *= -1
    style = random.choice(['plain','thousands','currency','paren','comma_dec','apos','spaced'])
    val = base
    if style == 'plain':
        return f"{val:.8f}"
    if style == 'thousands':
        return f"{val*1000:,.6f}"
    if style == 'currency':
        return f"${val*1000:,.2f}"
    if style == 'paren':
        if val >= 0:
            val = -val
        return f"({abs(val):.6f})"
    if style == 'comma_dec':
        s = f"{val*1000:,.2f}"  # 1,234.56
        s = s.replace(',', 'X').replace('.', ',').replace('X', '.')  # 1.234,56
        return s
    if style == 'apos':
        s = f"{val*1000:,.2f}"
        return s.replace(',', "'")
    if style == 'spaced':
        s = f"{val*1000:,.2f}"
        return s.replace(',', ' ')
    return f"{val:.8f}"


def pick_type():
    t = random.choice(TYPES)
    if random.random() < 0.2:
        t = t.upper() if random.random() < 0.5 else t.capitalize()
    return t


def maybe(value, prob=0.05, nulls=('', 'NA', None, 'n/a', '-')):
    return random.choice(nulls) if random.random() < prob else value


def gen_row(i):
    t = pick_type()
    base = random.choice(ASSETS)
    quote = random.choice(QUOTES)

    qty_allow_neg = t.lower() in ['sell','withdraw','fee','transfer_out']
    qty = rnd_amount(allow_negative=qty_allow_neg)
    total = rnd_amount(allow_negative=False)
    fee = rnd_amount(allow_negative=False, missing_prob=0.12)
    fee_ccy = random.choice(['USDT','USD','BNB','USDC',''])

    base_fmt = base if random.random() > 0.1 else base.lower()
    base_fmt = base_fmt if random.random() > 0.1 else f" {base_fmt} "

    row = {
        'time': rnd_time(i) if random.random() > 0.03 else maybe(rnd_time(i), prob=1.0),
        'type': t if random.random() > 0.03 else maybe(t, prob=1.0),
        'base-asset': base_fmt if random.random() > 0.03 else maybe(base_fmt, prob=1.0),
        'quantity': qty if random.random() > 0.05 else maybe(qty, prob=1.0),
        'quote-asset': quote if random.random() > 0.05 else maybe(quote, prob=1.0),
        'total': total if random.random() > 0.08 else maybe(total, prob=1.0),
        'fee': fee if random.random() > 0.12 else maybe(fee, prob=1.0),
        'fee-currency': fee_ccy if random.random() > 0.08 else maybe(fee_ccy, prob=1.0),
    }

    if random.random() < 0.02:
        row['type'] = random.choice(['CONVERT','Reward','DUST','bonus','Liquidity'])
    return row


def make_rows(n=480):
    rows = []
    for i in range(n):
        r = gen_row(i)
        rows.append(r)
        if i > 0 and i % 60 == 0:
            rows.append(rows[-1].copy())
        if random.random() < 0.03:
            rows.append(gen_row(i))
    return rows[:n]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rows = make_rows(480)
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(OUTPUT_FILE)


if __name__ == '__main__':
    main()
