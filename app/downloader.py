import datetime
import pandas as pd
from binance_historical_data import BinanceDataDumper

# --- Configuration (Move all configuration outside the guard) ---
symbol = 'BTCUSDT'
asset_class = 'um' # USD-M Futures (for USDT pairs)
data_type = 'trades'
start_date = datetime.date(2025, 12, 1) # Set a start date that is clearly before today
end_date = datetime.date.today() # The end date will be today

# ---------------------------------------------------------------

# 🚀 CRITICAL FIX: Wrap the code that spawns processes in the main guard
if __name__ == '__main__':
    # Initialize the data dumper
    data_dumper = BinanceDataDumper(
        path_dir_where_to_dump='./historical_data',
        asset_class=asset_class,
        data_type=data_type,
        data_frequency='daily'
    )

    print(f"Starting download for {symbol} {data_type} data from {start_date} to {end_date}...")

    # Run the download
    data_dumper.dump_data(
        tickers=[symbol],
        date_start=start_date,
        date_end=end_date, # Use the correct end_date variable
        is_to_update_existing=True
    )

    print(f"Download complete for {symbol}. Data saved in the './historical_data' folder.")
    
    # ... (Rest of your optional loading code goes here) ...