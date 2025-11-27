# main.py
import os
import argparse
import logging
from src import downloader
from src import backtester
from src.gcs_uploader import upload_file
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def run_download_then_backtest(csv_path: str, timeframe: str, bucket: str=None):
    logging.info("Reading trades from %s", csv_path)
    trades = downloader.read_trade_csv(csv_path)
    ohlc = downloader.trades_to_ohlc(trades, timeframe=timeframe)
    logging.info("Running backtest on %d rows", len(ohlc))
    stats, bt = backtester.run_backtest(ohlc)
    logging.info("Backtest results:\n%s", stats)
    # save ohlc and optionally upload chart CSV
    tmp_csv = "/tmp/ohlc.csv"
    ohlc.to_csv(tmp_csv, index=False)
    if bucket:
        dest = f"backtests/{os.path.basename(csv_path)}.ohlc.csv"
        upload_file(bucket, tmp_csv, dest)
        logging.info("Uploaded %s to gs://%s/%s", tmp_csv, bucket, dest)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to trade CSV to process")
    parser.add_argument("--timeframe", default="1min")
    parser.add_argument("--gcs-bucket", default=None, help="GCS bucket to upload results (optional)")
    args = parser.parse_args()
    run_download_then_backtest(args.csv, args.timeframe, args.gcs_bucket)

if __name__ == "__main__":
    main()
