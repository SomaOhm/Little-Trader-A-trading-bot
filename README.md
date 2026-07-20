# Algorithmic Trading Bot

A modular algorithmic trading system built around one core idea: **strategy, risk
management, and order execution should never depend on each other's
implementation details.** Each layer talks to the next through an interface, not
a concrete class, so any one of them can be replaced without touching the
others.

## Why this architecture

A naive trading bot is one script: fetch price -> check a condition -> place an
order. That works until you want to try a second strategy, or add a stop-loss,
or switch brokers -- at which point the "one script" has to be rewritten from
scratch, and it's easy to accidentally break risk controls while changing
strategy logic (or vice versa).

This project separates those concerns explicitly:

```
 MarketDataFeed          Strategy               RiskManager           Broker
 (fetches prices)  --->  (decides signal)  --->  (approves/vetoes) --> (places order)
                                                                            |
                                                                            v
                                                                     PositionStore
                                                                     (records trade)
```

- **`src/strategy/base.py`** defines the `Strategy` interface. `MeanReversionStrategy`
  is the v1 implementation (a z-score-based rule). A future ML-based strategy
  implements the same interface and drops in without changing risk or execution
  code at all.
- **`src/risk/risk_manager.py`** is intentionally independent of strategy. It only
  knows account equity, position size, and loss limits -- it doesn't know or
  care what logic produced a signal. This means a strategy change can never
  accidentally disable a safety limit.
- **`src/execution/broker.py`** defines the `Broker` interface; `AlpacaBroker` is
  the current implementation. A second broker would live in its own file and
  implement the same contract.
- **`src/portfolio/position_store.py`** keeps the bot's own record of trades in
  SQLite, independent of the broker's own account history.
- **`src/bot.py`** is the orchestrator. It's deliberately thin -- it wires the
  layers together and runs the loop, with no trading logic of its own.

## Status

Currently implements a rule-based mean-reversion strategy against Alpaca's
paper trading API. Not yet backtested at scale or run live for an extended
period -- treat current results as unvalidated until backtest numbers are
added below.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your Alpaca paper-trading keys
python -m src.bot
```

## Running tests

```bash
python -m pytest tests/ -v
```

Tests run entirely against fake price data -- no API keys required. This is
possible specifically because the strategy and risk layers don't depend on
the broker.

## Roadmap

- [ ] Backtesting harness against historical data (quantify return / Sharpe ratio)
- [ ] ML-based strategy implementation (`src/strategy/ml_strategy.py`) as a second
      `Strategy` implementation
- [ ] Proper daily equity baseline (currently re-baselines every run, not once
      per calendar day)
- [ ] Logging/alerting instead of print statements
