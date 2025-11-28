import datetime
import pandas as pd
from binance_historical_data import BinanceDataDumper

# --- Configuration ---
# 1. Choose your trading pair (e.g., BTCUSDT Perpetual Futures)
symbol = 'BTCUSDT'
# 2. Set the asset class to USD-M Futures ('um' for USD-M, 'cm' for Coin-M)
# NOTE: Since you specified Coin-M USDT, we will use 'um' (USD-M futures) for simplicity, 
# as USDT-M is the most common for retail futures scalping.
asset_class = 'um' 
data_type = 'trades' # 'trades' gives you tick-by-tick data, which is essential for scalping
start_date = datetime.date(2025, 12, 2) # Start date for data download
end_date = datetime.date.today()

# ---------------------

# Initialize the data dumper
data_dumper = BinanceDataDumper(
    path_dir_where_to_dump='./historical_data',
    asset_class=asset_class,
    data_type=data_type,
    data_frequency='daily' # Download data in daily files
)

print(f"Starting download for {symbol} {data_type} data from {start_date} to {end_date}...")

# Run the download
data_dumper.dump_data(
    tickers=[symbol],
    date_start=start_date,
    date_end=end_date,
    is_to_update_existing=True # Update existing files if needed
)

print(f"Download complete. Data saved in the './historical_data' folder.")

# Optional: Load and inspect the first file
# Find the first downloaded file path, assuming the daily file structure
try:
    # This path assumes the default folder structure created by the dumper
    first_file_path = f'./historical_data/{asset_class}/{data_type}/{symbol}/{symbol}-{end_date.strftime("%Y-%m-%d")}.zip'
    df = pd.read_csv(first_file_path, compression='zip')
    print("\n--- First 5 rows of downloaded trade data ---")
    print(df.head())
    print(f"Total trades in sample file: {len(df)}")
except FileNotFoundError:
    print("Could not find and load the sample file. Check your download path.")