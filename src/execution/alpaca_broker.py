"""
Alpaca implementation of the Broker interface. This is the only file
that should ever import Alpaca's SDK -- if you add a second broker
later, it gets its own file here and implements the same Broker
contract, and nothing in strategy/ or risk/ has to change.
"""
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from src.execution.broker import Broker, OrderResult


class AlpacaBroker(Broker):
    def __init__(self, api_key: str, api_secret: str, paper: bool = True):
        self._client = TradingClient(api_key, api_secret, paper=paper)

    def get_equity(self) -> float:
        account = self._client.get_account()
        return float(account.equity)

    def get_position_qty(self, symbol: str) -> float:
        try:
            position = self._client.get_open_position(symbol)
            return float(position.qty)
        except Exception:
            return 0.0

    def place_market_order(self, symbol: str, qty: float, side: str) -> OrderResult:
        order_side = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL
        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=order_side,
            time_in_force=TimeInForce.DAY,
        )
        order = self._client.submit_order(request)
        return OrderResult(
            order_id=str(order.id),
            symbol=order.symbol,
            side=side,
            qty=qty,
            status=str(order.status),
        )
