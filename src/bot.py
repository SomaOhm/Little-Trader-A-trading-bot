"""
Orchestrator. Deliberately thin: it wires the five layers together and
runs the loop, but contains no trading logic itself. If this file is
getting complicated, that's a sign logic is leaking into the wrong
place.
"""
import os
import time

from dotenv import load_dotenv

from src.data.market_data import MarketDataFeed
from src.strategy.mean_reversion import MeanReversionStrategy
from src.strategy.base import Signal
from src.risk.risk_manager import RiskManager, RiskLimits
from src.execution.alpaca_broker import AlpacaBroker
from src.portfolio.position_store import PositionStore

load_dotenv()

SYMBOLS = ["AAPL", "MSFT", "SPY"]
TRADE_QTY = 1  # shares per trade -- keep small while paper trading


def run_once(data_feed, strategy, risk_manager, broker, store) -> None:
    equity = broker.get_equity()
    risk_manager.start_of_day(equity)  # naive for now -- re-baselines each run

    for symbol in SYMBOLS:
        bars = data_feed.get_recent_bars(symbol)
        signal = strategy.decide(symbol, bars)
        print(f"[check] {symbol} @ {current_price:.2f} -> {signal.value}")

        if signal == Signal.HOLD:
            continue

        current_price = bars[-1].close
        proposed_value = current_price * TRADE_QTY

        if not risk_manager.approve_trade(equity, proposed_value):
            print(f"[risk] blocked {signal.value} {symbol} -- risk limits not satisfied")
            continue

        result = broker.place_market_order(symbol, TRADE_QTY, signal.value)
        store.record_trade(symbol, signal.value, TRADE_QTY, current_price, result.order_id, result.status)
        print(f"[trade] {signal.value} {TRADE_QTY} {symbol} @ ~{current_price:.2f} -> {result.status}")


def main() -> None:
    api_key = os.environ["ALPACA_API_KEY"]
    api_secret = os.environ["ALPACA_API_SECRET"]

    data_feed = MarketDataFeed(api_key, api_secret)
    strategy = MeanReversionStrategy()
    risk_manager = RiskManager(RiskLimits())
    broker = AlpacaBroker(api_key, api_secret, paper=True)
    store = PositionStore("data/trades.db")

    print("Starting trading bot (paper trading)...")
    while True:
        run_once(data_feed, strategy, risk_manager, broker, store)
        time.sleep(60 * 15)  # check every 15 minutes -- tune later


if __name__ == "__main__":
    main()
