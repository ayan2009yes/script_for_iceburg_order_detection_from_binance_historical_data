"""
Fast iceberg detector (chunked + vectorized)
Saves top-10 price levels with side classification to CSV.
"""

import pandas as pd
import os

# ---------- USER SETTINGS ----------
INPUT_FILE = r"C:\Users\madeo\OneDrive\Desktop\scripts for trading\BTCUSDT-trades-2025-09.csv"
OUTPUT_FILE = r"C:\Users\madeo\Downloads\BNBUSDT-aggTrades-2025-09-09\bababaT-iceberg-top10-withde.csv"

# Tune this depending on RAM. 200_000-1_000_000 are common values.
CHUNKSIZE = 300_000

# How many decimals to treat price as (2 -> cents). Increase for tighter grouping.
PRICE_DECIMALS = 2
# -----------------------------------

def parse_bool(x):
    """Robust converter for is_buyer_maker column (handles 'true'/'false' strings)."""
    try:
        if isinstance(x, bool):
            return x
        s = str(x).strip().lower()
        return s in ("true", "1", "t", "yes", "y")
    except Exception:
        return False

def main():
    # columns we need (reduce memory)
    usecols = ['id', 'price', 'qty', 'quote_qty', 'is_buyer_maker']

    aggregated = None  # will hold running aggregate as DataFrame

    price_multiplier = 10 ** PRICE_DECIMALS

    reader = pd.read_csv(
        INPUT_FILE,
        usecols=usecols,
        converters={'is_buyer_maker': parse_bool},
        dtype={'id': 'int64', 'price': 'float64', 'qty': 'float64', 'quote_qty': 'float64'},
        chunksize=CHUNKSIZE,
        low_memory=True,
    )

    print("Processing chunks...")
    for chunk_idx, chunk in enumerate(reader, start=1):
        # create integer price key (e.g., price 1008.77 -> 100877 if PRICE_DECIMALS=2)
        chunk['price_key'] = (chunk['price'] * price_multiplier).round().astype('int64')

        # Ensure numeric
        chunk['qty'] = chunk['qty'].astype('float64', copy=False)
        chunk['quote_qty'] = chunk['quote_qty'].astype('float64', copy=False)

        # Vectorized buy/sell split (no apply)
        # is_buyer_maker == False => buyer is taker => buyer-initiated trade => buy_qty
        chunk['buy_qty'] = chunk['qty'] * (~chunk['is_buyer_maker']).astype('int8')
        chunk['sell_qty'] = chunk['qty'] * (chunk['is_buyer_maker']).astype('int8')

        # Group by price_key for this chunk
        grp = chunk.groupby('price_key', sort=False).agg(
            trade_count=('id', 'count'),
            qty=('qty', 'sum'),
            quote_qty=('quote_qty', 'sum'),
            buy_qty=('buy_qty', 'sum'),
            sell_qty=('sell_qty', 'sum'),
        )

        # Accumulate
        if aggregated is None:
            aggregated = grp
        else:
            # element-wise add; fill missing with 0
            aggregated = aggregated.add(grp, fill_value=0)

        # Optional progress info
        if chunk_idx % 5 == 0:
            print(f"  processed {chunk_idx} chunks ...")

    if aggregated is None:
        print("No data found in file or file is empty.")
        return

    # Finalize aggregated DataFrame
    aggregated = aggregated.reset_index().rename(columns={'price_key': 'price_key_int'})

    # Convert price_key back to human price
    aggregated['price'] = aggregated['price_key_int'] / price_multiplier

    # Compute buy/sell percentages (handle qty==0)
    aggregated['buy_pct'] = (aggregated['buy_qty'] / aggregated['qty']).fillna(0) * 100
    aggregated['sell_pct'] = (aggregated['sell_qty'] / aggregated['qty']).fillna(0) * 100

    # Classify iceberg side:
    # - buy_qty > sell_qty  => buyers are takers => iceberg located on sell side (hidden sells)
    # - sell_qty > buy_qty  => sellers are takers => iceberg located on buy side (hidden buys)
    def classify_row(r):
        if r['buy_qty'] > r['sell_qty']:
            return "Sell-side Iceberg (buyers taker)"
        elif r['sell_qty'] > r['buy_qty']:
            return "Buy-side Iceberg (sellers taker)"
        else:
            return "Neutral/Unclear"

    aggregated['iceberg_side'] = aggregated.apply(classify_row, axis=1)

    # Sort by frequency (most repeated small fills)
    aggregated = aggregated.sort_values(by='trade_count', ascending=False)

    # Format/round columns for readability
    out = aggregated.head(50).copy()  # keep extra in-memory if user wants to inspect more; we'll save top10
    out['price'] = out['price'].round(PRICE_DECIMALS)
    out['qty'] = out['qty'].round(3)
    out['quote_qty'] = out['quote_qty'].round(2)
    out['buy_qty'] = out['buy_qty'].round(3)
    out['sell_qty'] = out['sell_qty'].round(3)
    out['buy_pct'] = out['buy_pct'].round(1)
    out['sell_pct'] = out['sell_pct'].round(1)
    out['trade_count'] = out['trade_count'].astype(int)

    top10 = out.head(10).loc[:, ['price', 'trade_count', 'qty', 'quote_qty', 'buy_qty', 'sell_qty', 'buy_pct', 'sell_pct', 'iceberg_side']]

    # Save top10
    top10.to_csv(OUTPUT_FILE, index=False)
    print("\nTop-10 iceberg candidates (saved):")
    print(top10.to_string(index=False))
    print(f"\nSaved CSV -> {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
