import sqlite3
import os
import contextlib
from typing import List, Optional
from src.models import Transaction

class Database:
    """Local SQLite repository for personal finance records."""

    def __init__(self, db_path: str = "finance.db"):
        self.db_path = db_path
        self._init_db()

    @contextlib.contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self):
        """Initialize tables and indexes with WAL mode enabled."""
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with self._connection() as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    payee TEXT NOT NULL,
                    raw_description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL DEFAULT 'Uncategorized',
                    confidence REAL NOT NULL DEFAULT 0.0,
                    account TEXT NOT NULL DEFAULT 'Checking',
                    notes TEXT
                );
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
            """)

    def insert_transaction(self, t: Transaction) -> int:
        with self._connection() as conn:
            cursor = conn.execute("""
                INSERT INTO transactions (date, payee, raw_description, amount, category, confidence, account, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (t.date, t.payee, t.raw_description, t.amount, t.category, t.confidence, t.account, t.notes))
            return cursor.lastrowid

    def insert_transactions(self, transactions: List[Transaction]) -> int:
        """Batch insert transactions."""
        count = 0
        with self._connection() as conn:
            for t in transactions:
                conn.execute("""
                    INSERT INTO transactions (date, payee, raw_description, amount, category, confidence, account, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (t.date, t.payee, t.raw_description, t.amount, t.category, t.confidence, t.account, t.notes))
                count += 1
        return count

    def get_all_transactions(self) -> List[Transaction]:
        with self._connection() as conn:
            rows = conn.execute("SELECT * FROM transactions ORDER BY date DESC, id DESC").fetchall()
            return [Transaction(**dict(row)) for row in rows]

    def update_transaction_category(self, tx_id: int, category: str, confidence: float):
        with self._connection() as conn:
            conn.execute("""
                UPDATE transactions SET category = ?, confidence = ? WHERE id = ?
            """, (category, confidence, tx_id))

    def clear(self):
        with self._connection() as conn:
            conn.execute("DELETE FROM transactions;")
