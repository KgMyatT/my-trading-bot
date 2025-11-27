# src/backtester.py
import pandas as pd
from backtesting import Backtest
from src.strategy import ScalperStrategy

def run_backtest(ohlc: pd.DataFrame, cash: float = 10000.0, commission: float = 0.0005):
    # Ensure columns have correct names
    df = ohlc.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })[['Open','High','Low','Close','Volume']].copy()
    bt = Backtest(df, ScalperStrategy, cash=cash, commission=commission, exclusive_orders=True)
    stats = bt.run()
    return stats, bt
