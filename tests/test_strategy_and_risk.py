"""
Tests run against fake data only -- no Alpaca credentials needed.
This is possible specifically because strategy and risk are decoupled
from the broker; that's the payoff of the architecture, made concrete.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.market_data import PriceBar
from src.strategy.mean_reversion import MeanReversionStrategy
from src.strategy.base import Signal
from src.risk.risk_manager import RiskManager, RiskLimits


def make_bars(closes):
    now = datetime.utcnow()
    return [
        PriceBar(timestamp=now - timedelta(days=len(closes) - i), open=c, high=c, low=c, close=c, volume=1000)
        for i, c in enumerate(closes)
    ]


def test_buy_signal_on_price_drop():
    # 19 stable bars, then a sharp drop -> should trigger BUY
    closes = [100.0] * 19 + [85.0]
    strategy = MeanReversionStrategy(lookback=20)
    signal = strategy.decide("TEST", make_bars(closes))
    assert signal == Signal.BUY


def test_sell_signal_on_price_spike():
    closes = [100.0] * 19 + [115.0]
    strategy = MeanReversionStrategy(lookback=20)
    signal = strategy.decide("TEST", make_bars(closes))
    assert signal == Signal.SELL


def test_hold_when_insufficient_history():
    strategy = MeanReversionStrategy(lookback=20)
    signal = strategy.decide("TEST", make_bars([100.0] * 5))
    assert signal == Signal.HOLD


def test_risk_manager_blocks_after_daily_loss_limit():
    risk = RiskManager(RiskLimits(max_daily_loss_pct=0.03))
    risk.start_of_day(equity=10000)
    assert risk.daily_loss_limit_breached(current_equity=9600) is True   # -4%
    assert risk.daily_loss_limit_breached(current_equity=9800) is False  # -2%


def test_risk_manager_blocks_oversized_position():
    risk = RiskManager(RiskLimits(max_position_size_pct=0.10))
    assert risk.position_size_allowed(position_value=500, total_equity=10000) is True   # 5%
    assert risk.position_size_allowed(position_value=1500, total_equity=10000) is False  # 15%
