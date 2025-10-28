# script_for_iceburg_order_detection_from_binance_historical_data
# 🧊 Iceberg Detector: Buy vs Sell Side (Fast + Vectorized)

## 📘 Overview

This Python script is a **high-speed iceberg order detector** designed for cryptocurrency trading data (e.g., Binance aggregated trade files). It detects **hidden buy/sell iceberg orders** by processing millions of trades efficiently in chunks and classifying price levels based on trade imbalance and frequency.

---

## ⚙️ Purpose

Iceberg orders are large hidden orders split into smaller visible ones to hide the trader's true intent. This script helps uncover those patterns by:

* Grouping trades at each price level.
* Comparing **buy vs sell volumes**.
* Highlighting **levels with abnormally high small-trade frequency** (potential iceberg zones).

---

## 📂 Input / Output

### **Input:**

CSV file containing Binance-style trade data, e.g.:

```
id,price,qty,quote_qty,is_buyer_maker
```

Example: `BTCUSDT-trades-2025-09.csv`

### **Output:**

CSV file containing the **Top 10 iceberg price levels**, e.g.:

```
price,trade_count,qty,quote_qty,buy_qty,sell_qty,buy_pct,sell_pct,iceberg_side
```

Example output file: `bababaT-iceberg-top10-withde.csv`

---

## 🧩 Key Features

### 🔹 **Chunked Processing**

* Handles massive trade datasets (millions of rows) efficiently using pandas `chunksize`.

### 🔹 **Vectorized Computation**

* Fully vectorized calculations (no loops), ensuring maximum speed.

### 🔹 **Buy/Sell Split**

* Accurately separates buyer/seller-initiated trades using the `is_buyer_maker` flag.

### 🔹 **Iceberg Classification**

* **Buyers takers → Sell-side Iceberg (hidden sells)**
* **Sellers takers → Buy-side Iceberg (hidden buys)**

### 🔹 **Top-10 Extraction**

* Outputs the 10 most suspicious price levels with iceberg activity.

---

## 🧠 How It Works

1. **Read the input file in chunks** (default: 300,000 rows per chunk).
2. **Generate integer price keys** for grouping (based on rounding precision).
3. **Split trades into buy/sell volumes** using `is_buyer_maker`.
4. **Aggregate trade statistics** per price level.
5. **Combine all chunks** into a single DataFrame.
6. **Calculate buy/sell percentages and classify iceberg side.**
7. **Sort and export top 10 iceberg levels to CSV.**

---

## 📊 Example Output

| Price    | Trades | Qty   | Buy% | Sell% | Iceberg Side      |
| -------- | ------ | ----- | ---- | ----- | ----------------- |
| 65120.00 | 493    | 12.34 | 70.2 | 29.8  | Sell-side Iceberg |
| 65115.50 | 471    | 11.89 | 28.7 | 71.3  | Buy-side Iceberg  |

---

## 🔧 Configuration

| Variable         | Description                          | Default        |
| ---------------- | ------------------------------------ | -------------- |
| `INPUT_FILE`     | Path to your trade data CSV          | *User-defined* |
| `OUTPUT_FILE`    | Path for saving top-10 iceberg CSV   | *User-defined* |
| `CHUNKSIZE`      | Number of rows processed at once     | `300_000`      |
| `PRICE_DECIMALS` | Decimal precision for price grouping | `2`            |

---

## 🚀 Usage

### **Run the script:**

```bash
python buyvsselliceburg.py
```

### **Console Output Example:**

```
Processing chunks...
  processed 5 chunks ...
Top-10 iceberg candidates (saved):

   price  trade_count  qty  buy_qty  sell_qty  buy_pct  sell_pct          iceberg_side
65120.0          493 12.34    8.65      3.69     70.2      29.8  Sell-side Iceberg
65115.5          471 11.89    3.41      8.48     28.7      71.3  Buy-side Iceberg

Saved CSV -> C:\Users\madeo\Downloads\BNBUSDT-aggTrades-2025-09-09\bababaT-iceberg-top10-withde.csv
```

---

## 🧾 Output Columns Explained

| Column         | Description                             |
| -------------- | --------------------------------------- |
| `price`        | Price level of aggregated trades        |
| `trade_count`  | Number of trades at that price level    |
| `qty`          | Total traded quantity                   |
| `quote_qty`    | Total quote volume (price × qty)        |
| `buy_qty`      | Total buyer-initiated volume            |
| `sell_qty`     | Total seller-initiated volume           |
| `buy_pct`      | % of total volume initiated by buyers   |
| `sell_pct`     | % of total volume initiated by sellers  |
| `iceberg_side` | Classified side of the detected iceberg |

---

## 💡 Tips for Better Accuracy

* Increase `PRICE_DECIMALS` for more granular grouping (e.g., `3` for tighter clustering).
* Increase `CHUNKSIZE` if you have more RAM for faster processing.
* Works best on **raw aggregated trades**, not already-aggregated OHLCV data.

---

## 🧰 Requirements

* Python 3.8+
* pandas >= 1.5

Install dependencies:

```bash
pip install pandas
```

---

## 🧩 Example Use Case

You can use this tool with Binance data (from the API or data dumps) to:

* Detect **hidden accumulation or distribution zones.**
* Identify **smart money behavior.**
* Enhance **quantitative trading strategies** based on hidden liquidity.

---

## 🧑‍💻 Author

**MD Ayan Umar**
A data-driven trader and developer focused on market microstructure analysis and trading automation.
