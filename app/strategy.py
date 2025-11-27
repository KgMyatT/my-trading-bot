# src/strategy.py
from backtesting import Strategy
import pandas as pd
import numpy as np

class ScalperStrategy(Strategy):
    """
    Simple example scalper: uses moving-average crossover on close price.
    Replace this with your real logic.
    """
    def init(self):
        close = self.data.Close
        self.short_ma = self.I(pd.Series.rolling, close, window=5).shift(0)
        self.long_ma = self.I(pd.Series.rolling, close, window=20).shift(0)

    def next(self):
        if self.short_ma[-1] > self.long_ma[-1] and not self.position:
            self.buy()
        elif self.short_ma[-1] < self.long_ma[-1] and self.position:
            self.position.close()
