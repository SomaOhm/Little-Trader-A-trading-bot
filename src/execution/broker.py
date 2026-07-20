"""
Broker interface.

Job: place orders and report account/position state. Strategy and risk
layers only ever talk to this interface -- never to a specific broker's
SDK directly. AlpacaBroker is the first implementation; a second broker
could be added later by implementing this same contract.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class OrderResult:
    order_id: str
    symbol: str
    side: str
    qty: float
    status: str


class Broker(ABC):
    @abstractmethod
    def get_equity(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def get_position_qty(self, symbol: str) -> float:
        """Returns 0 if no open position."""
        raise NotImplementedError

    @abstractmethod
    def place_market_order(self, symbol: str, qty: float, side: str) -> OrderResult:
        raise NotImplementedError
