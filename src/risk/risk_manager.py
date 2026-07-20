"""
Risk manager.

Job: veto trades that violate account-level safety rules, regardless
of which strategy produced the signal. This is intentionally NOT part
of the strategy -- swapping mean-reversion for an ML model must never
require re-implementing loss limits.
"""
from dataclasses import dataclass


@dataclass
class RiskLimits:
    max_daily_loss_pct: float = 0.03      # halt trading if down 3% today
    max_position_size_pct: float = 0.10   # no single position > 10% of equity
    stop_loss_pct: float = 0.05           # exit a position down 5% from entry


class RiskManager:
    def __init__(self, limits: RiskLimits):
        self.limits = limits
        self._starting_equity_today: float | None = None

    def start_of_day(self, equity: float) -> None:
        self._starting_equity_today = equity

    def daily_loss_limit_breached(self, current_equity: float) -> bool:
        if self._starting_equity_today is None:
            return False
        drawdown = (self._starting_equity_today - current_equity) / self._starting_equity_today
        return drawdown >= self.limits.max_daily_loss_pct

    def position_size_allowed(self, position_value: float, total_equity: float) -> bool:
        if total_equity <= 0:
            return False
        return (position_value / total_equity) <= self.limits.max_position_size_pct

    def stop_loss_triggered(self, entry_price: float, current_price: float) -> bool:
        loss_pct = (entry_price - current_price) / entry_price
        return loss_pct >= self.limits.stop_loss_pct

    def approve_trade(self, current_equity: float, proposed_position_value: float) -> bool:
        """Single choke point every order passes through before execution."""
        if self.daily_loss_limit_breached(current_equity):
            return False
        if not self.position_size_allowed(proposed_position_value, current_equity):
            return False
        return True
