"""
Rule-based mean-reversion strategy: buys when price is significantly
below its recent rolling average (z-score negative beyond threshold),
sells when significantly above. This is the v1 "brain" -- swap it for
src/strategy/ml_strategy.py later without touching anything else.
"""
import statistics
from typing import List

from src.data.market_data import PriceBar
from src.strategy.base import Signal, Strategy


class MeanReversionStrategy(Strategy):
    def __init__(self, lookback: int = 20, entry_z: float = 1.5, exit_z: float = 0.25):
        self.lookback = lookback
        self.entry_z = entry_z
        self.exit_z = exit_z

    def decide(self, symbol: str, bars: List[PriceBar]) -> Signal:
        if len(bars) < self.lookback:
            return Signal.HOLD  # not enough history yet

        closes = [b.close for b in bars[-self.lookback:]]
        mean = statistics.mean(closes)
        stdev = statistics.pstdev(closes)
        if stdev == 0:
            return Signal.HOLD

        current_price = closes[-1]
        z_score = (current_price - mean) / stdev

        if z_score <= -self.entry_z:
            return Signal.BUY
        elif z_score >= self.entry_z:
            return Signal.SELL
        elif abs(z_score) <= self.exit_z:
            return Signal.HOLD  # reverted to mean, no strong signal either way

        return Signal.HOLD
