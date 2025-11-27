import os
import pandas as pd
import glob
import zipfile
from binance_historical_data import BinanceDataDumper
import datetime

SYMBOL = "BTCUSDT"
START_DATE = datetime.date(2024, 8, 1)
END_DATE = datetime.date(2024, 11, 1)
RAW_DATA_DIR = "/home/raw_data"
OUTPUT_DIR = "/home/lean/data/crypto/binance/minute/btcusdt"

# 1. Download
print(f"--- Downloading Raw Data ---")
dumper = BinanceDataDumper(path_dir_where_to_dump=RAW_DATA_DIR, asset_class="um", data_type="klines", data_frequency="1m")
dumper.dump_data(tickers=[SYMBOL], date_start=START_DATE, date_end=END_DATE, is_to_update_existing=True)

# 2. Convert
print(f"--- Converting to LEAN Format ---")
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

# Look in FUTURES folder
files = glob.glob(f"{RAW_DATA_DIR}/futures/um/daily/klines/{SYMBOL}/1m/*.csv")
print(f"Found {len(files)} files.")

for file_path in files:
    try:
        # Parse Date: BTCUSDT-1m-2024-11-01.csv
        filename = os.path.basename(file_path)
        date_part = filename.replace(f"{SYMBOL}-1m-", "").replace(".csv", "")
        date_obj = datetime.datetime.strptime(date_part, "%Y-%m-%d")
        lean_date = date_obj.strftime("%Y%m%d")

        # Read CSV (Force numeric, drop bad rows)
        df = pd.read_csv(file_path, header=None)
        df[0] = pd.to_numeric(df[0], errors='coerce') # Time column
        df = df.dropna(subset=[0])
        
        # LEAN Format: ms_since_midnight, open, high, low, close, volume
        lean_df = pd.DataFrame()
        lean_df['time'] = (df[0].astype(int) % 86400000)
        lean_df['open'] = df[1]
        lean_df['high'] = df[2]
        lean_df['low'] = df[3]
        lean_df['close'] = df[4]
        lean_df['volume'] = df[5]

        # Save as Zip
        zip_name = f"{OUTPUT_DIR}/{lean_date}_trade.zip"
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{lean_date}_{SYMBOL.lower()}_minute_trade.csv", lean_df.to_csv(header=False, index=False))
            
    except Exception as e:
        print(f"Error on {file_path}: {e}")

print("--- Data Done ---")