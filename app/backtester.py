import pandas as pd
import os
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# ==============================================================================
# 1. DATA PREPARATION FUNCTIONS (No changes here)
# ==============================================================================

def load_and_combine_trades(base_path, symbol, asset_class):
    """
    Loads all daily trade files, combines them, and cleans the DataFrame.
    """
    trades_list = []
    
    TRADE_COLUMNS = ['id', 'price', 'qty', 'quoteQty', 'time', 'isBuyerMaker']
    USE_COLS = ['time', 'price', 'qty', 'quoteQty', 'isBuyerMaker']
    
    data_dir = os.path.join(base_path, 'futures', asset_class, 'daily', 'trades', symbol)

    if not os.path.exists(data_dir):
        print(f"Error: Data directory not found at {data_dir}. Check your download path.")
        return None

    for filename in os.listdir(data_dir):
        if filename.endswith('.zip') or (filename.endswith('.csv') and 'trades' in filename):
            file_path = os.path.join(data_dir, filename)
            
            try:
                df = pd.read_csv(
                    file_path, 
                    compression='zip' if filename.endswith('.zip') else None,
                    header=None,           
                    names=TRADE_COLUMNS,   
                    usecols=USE_COLS       
                )
                trades_list.append(df)
            except Exception as e:
                print(f"Skipping file {filename} due to error: {e}")
                
    if not trades_list:
        print("No trade data found. Please ensure the download completed successfully.")
        return None
        
    all_trades = pd.concat(trades_list, ignore_index=True)

    all_trades['time'] = pd.to_numeric(all_trades['time'], errors='coerce')
    all_trades = all_trades.dropna(subset=['time'])
    
    all_trades['timestamp'] = pd.to_datetime(all_trades['time'], unit='ms')
    all_trades = all_trades.set_index('timestamp')
    
    all_trades = all_trades[['price', 'qty', 'quoteQty', 'isBuyerMaker']] 
    
    all_trades['price'] = pd.to_numeric(all_trades['price'], errors='coerce')
    all_trades['qty'] = pd.to_numeric(all_trades['qty'], errors='coerce')
    all_trades = all_trades.dropna(subset=['price', 'qty']) 
    
    print(f"Successfully loaded and combined {len(all_trades)} trades.")
    return all_trades.sort_index()


def calculate_obi_proxy(trades_df, window='5s'):
    """
    Calculates the Order Book Imbalance (OBI) Proxy based on directional volume.
    """
    if 'isBuyerMaker' not in trades_df.columns:
        print("ERROR: 'isBuyerMaker' column missing. Cannot calculate OBI proxy.")
        return pd.Series(0, index=trades_df.index)

    trades_df['buy_vol'] = trades_df.apply(
        lambda row: row['qty'] if not row['isBuyerMaker'] else 0, axis=1
    )
    trades_df['sell_vol'] = trades_df.apply(
        lambda row: row['qty'] if row['isBuyerMaker'] else 0, axis=1
    )

    rolling_buy_vol = trades_df['buy_vol'].resample(window).sum()
    rolling_sell_vol = trades_df['sell_vol'].resample(window).sum()
    
    total_vol = rolling_buy_vol + rolling_sell_vol
    obi_score = (rolling_buy_vol - rolling_sell_vol) / total_vol.replace(0, 1) 
    
    return obi_score.rename('OBI').fillna(0) 


def resample_trades_to_ohlcv(trades_df, interval='1Min'):
    """
    Resamples raw trade data into Open-High-Low-Close-Volume (OHLCV) bars.
    """
    if trades_df is None:
        return None

    ohlc = trades_df['price'].resample(interval).ohlc()
    volume = trades_df['qty'].resample(interval).sum()
    ohlcv = pd.concat([ohlc, volume.rename('Volume')], axis=1)
    
    ohlcv = ohlcv.dropna()
    ohlcv.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    print(f"Resampling complete. Total {len(ohlcv)} bars created at {interval} interval.")
    return ohlcv


# ==============================================================================
# 2. --- NEW "SMART" AI STRATEGY CLASS ---
# ==============================================================================

class TrendOBIScalper(Strategy):
    """
    A "smart" scalping strategy that combines two signals:
    1. SIGNAL: Order Book Imbalance (OBI) for a 5-second entry trigger.
    2. FILTER: A long-term EMA to define the "trend regime".
    """
    
    # --- Parameters to Optimize ---
    # We will let the optimizer find the best values for these
    ema_period = 200        # The period for our long-term trend filter
    obi_threshold = 0.1     # The trigger level for our OBI signal
    sl_percent = 0.0005     # Stop Loss
    tp_percent = 0.001      # Take Profit

    def init(self):
        # 1. Access the OBI score we calculated
        try:
            self.obi_score = self.data.OBI
        except AttributeError:
            print("ERROR: 'OBI' column not found in data. Strategy will not trade.")
            self.obi_score = [0] * len(self.data.Close)

        # 2. --- NEW: Create the Trend Filter ---
        # We use a lambda function to calculate the Exponential Moving Average (EMA)
        self.trend_ema = self.I(
            lambda x: pd.Series(x).ewm(span=self.ema_period, adjust=False).mean(),
            self.data.Close,
            name="Trend_EMA"
        )

    def next(self):
        # Get the most recent values
        current_close = self.data.Close[-1]
        current_obi = self.obi_score[-1]
        current_ema = self.trend_ema[-1]
        
        # --- FSM: Only trade if we are "IDLE" (no open position) ---
        if not self.position:
            
            # --- NEW "SMART" LOGIC ---
            
            # 1. Bullish Regime: Price is ABOVE the trend line
            if current_close > current_ema:
                # We are only "allowed" to look for BUY signals
                if current_obi > self.obi_threshold:
                    # Both conditions met! Place the trade.
                    sl_price = current_close * (1 - self.sl_percent)
                    tp_price = current_close * (1 + self.tp_percent)
                    self.buy(sl=sl_price, tp=tp_price)
            
            # 2. Bearish Regime: Price is BELOW the trend line
            elif current_close < current_ema:
                # We are only "allowed" to look for SELL signals
                if current_obi < -self.obi_threshold:
                    # Both conditions met! Place the trade.
                    sl_price = current_close * (1 + self.sl_percent)
                    tp_price = current_close * (1 - self.tp_percent)
                    self.sell(sl=sl_price, tp=tp_price)


# ==============================================================================
# 3. MAIN EXECUTION (Updated for new Strategy and Optimization)
# ==============================================================================

if __name__ == "__main__":
    
    # --- 1. Configuration ---
    BASE_DATA_PATH = r'C:\Users\kaung myat\AutoTrading\historical_data'
    SYMBOL = 'BTCUSDT'
    ASSET_CLASS = 'um' 
    SCALPING_INTERVAL = '5s' # Use lowercase 's' (fix from FutureWarning)

    # --- 2. Load and Prepare the Data ---
    print("Loading raw trade data...")
    all_trades_df = load_and_combine_trades(BASE_DATA_PATH, SYMBOL, ASSET_CLASS)

    data = None
    if all_trades_df is not None:
        print("Calculating OBI proxy score...")
        obi_score_series = calculate_obi_proxy(all_trades_df, window=SCALPING_INTERVAL)
        
        print(f"Resampling raw trades to {SCALPING_INTERVAL} OHLCV bars...")
        data = resample_trades_to_ohlcv(all_trades_df, interval=SCALPING_INTERVAL)

        if data is not None:
            data['OBI'] = obi_score_series
            data = data.dropna() 
            print("Data preparation complete. OBI score attached.")
    
    # --- 3. Run Optimization ---
    if data is not None and not data.empty:
        print("Starting OPTIMIZATION with new Trend Filter...")
        bt = Backtest(
            data,
            TrendOBIScalper, # --- NEW: Use our new strategy class ---
            cash=100_000,
            commission=0.0004, 
            margin=1/20,       
            exclusive_orders=True
        )

        # --- NEW: Update optimization to test our new parameters ---
        # This will be slower, as there are more combinations
        stats = bt.optimize(
            # Let's test a wider range for OBI
            obi_threshold=[0.1, 0.25, 0.4],
            sl_percent=[0.001],           # Let's fix SL and TP for now to speed it up
            tp_percent=[0.0015],
            # --- NEW: Test two different trend lengths ---
            ema_period=[100, 200], # Test a "faster" trend and a "slower" trend
            maximize='Equity Final [$]'
        )
        
        print("Optimization Complete!")
        print(stats)
        
        # Print the parameters of the best-performing strategy
        print("\n--- Best Strategy Parameters ---")
        print(stats._strategy)

        # Plot the best-performing strategy
        bt.plot()
        
    else:
        print("="*50)
        print("FATAL ERROR: Data loading failed. Backtest cannot run.")
        print("="*50)