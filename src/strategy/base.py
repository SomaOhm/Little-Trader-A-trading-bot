"""
Strategy interface.

Job: decide buy / sell / hold given price history. This is the "brain"
boundary -- anything that implements decide() can be swapped in without
touching risk management, execution, or data fetching. A rule-based
mean-reversion strategy and an ML classifier both satisfy this same
contract.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import List

from src.data.market_data import PriceBar


class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Strategy(ABC):
    @abstractmethod
    def decide(self, symbol: str, bars: List[PriceBar]) -> Signal:
        """Given recent price bars for a symbol, return a trading signal."""
        raise NotImplementedError
