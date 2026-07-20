"""
Position store.

Job: persist what trades were made and when, independent of the broker's
own records, so the bot has its own audit trail. SQLite is enough for a
single-instance bot -- swap for Postgres later if this ever runs
distributed.
"""
import sqlite3
from datetime import datetime
from pathlib import Path


class PositionStore:
    def __init__(self, db_path: str = "trades.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                qty REAL NOT NULL,
                price REAL,
                order_id TEXT,
                status TEXT
            )
            """
        )
        self._conn.commit()

    def record_trade(self, symbol: str, side: str, qty: float, price: float, order_id: str, status: str) -> None:
        self._conn.execute(
            "INSERT INTO trades (timestamp, symbol, side, qty, price, order_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), symbol, side, qty, price, order_id, status),
        )
        self._conn.commit()

    def get_trade_history(self, symbol: str | None = None) -> list[sqlite3.Row]:
        self._conn.row_factory = sqlite3.Row
        cur = self._conn.cursor()
        if symbol:
            cur.execute("SELECT * FROM trades WHERE symbol = ? ORDER BY timestamp DESC", (symbol,))
        else:
            cur.execute("SELECT * FROM trades ORDER BY timestamp DESC")
        return cur.fetchall()

    def close(self) -> None:
        self._conn.close()
