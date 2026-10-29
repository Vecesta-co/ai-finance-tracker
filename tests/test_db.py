import os
import tempfile
import pytest
from src.db import Database
from src.models import Transaction

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = Database(path)
    yield db
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

def test_db_insert_and_get(temp_db):
    t = Transaction(
        date="2026-01-01",
        payee="Trader Joe's",
        raw_description="TRADER JOE #123",
        amount=-55.40,
        category="Groceries"
    )
    row_id = temp_db.insert_transaction(t)
    assert row_id is not None

    txs = temp_db.get_all_transactions()
    assert len(txs) == 1
    assert txs[0].payee == "Trader Joe's"
    assert txs[0].amount == -55.40

def test_db_batch_insert(temp_db):
    batch = [
        Transaction(date="2026-01-01", payee=f"Payee {i}", raw_description="raw", amount=-10.0 * i)
        for i in range(1, 6)
    ]
    count = temp_db.insert_transactions(batch)
    assert count == 5
    assert len(temp_db.get_all_transactions()) == 5

def test_db_update_category(temp_db):
    t = Transaction(date="2026-01-01", payee="Unknown", raw_description="raw", amount=-20.0)
    tx_id = temp_db.insert_transaction(t)
    temp_db.update_transaction_category(tx_id, "Shopping", 0.9)

    txs = temp_db.get_all_transactions()
    assert txs[0].category == "Shopping"
    assert txs[0].confidence == 0.9

def test_db_clear(temp_db):
    t = Transaction(date="2026-01-01", payee="Test", raw_description="raw", amount=-1.0)
    temp_db.insert_transaction(t)
    assert len(temp_db.get_all_transactions()) == 1
    temp_db.clear()
    assert len(temp_db.get_all_transactions()) == 0
