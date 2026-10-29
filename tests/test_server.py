import urllib.request
import json
import time
import os
import tempfile
import pytest
from src.db import Database
from src.importer import StatementImporter
from src.categorizer import TransactionCategorizer
from src.server import run_server

@pytest.fixture(scope="module")
def server_setup():
    port = 8765
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = Database(db_path)
    txs = StatementImporter.import_csv("fixtures/sample_bank_statement.csv")
    TransactionCategorizer().categorize_batch(txs)
    db.insert_transactions(txs)

    server = run_server(db=db, host="127.0.0.1", port=port, background=True)
    time.sleep(0.5)
    url = f"http://127.0.0.1:{port}"
    yield url
    server.shutdown()
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except Exception:
        pass

def test_server_health(server_setup):
    with urllib.request.urlopen(f"{server_setup}/health") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data["status"] == "ok"

def test_server_dashboard(server_setup):
    with urllib.request.urlopen(f"{server_setup}/") as resp:
        assert resp.status == 200
        html = resp.read().decode()
        assert "AI Finance Tracker" in html

def test_server_api_summary(server_setup):
    with urllib.request.urlopen(f"{server_setup}/api/summary") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert "total_income" in data
        assert "total_expenses" in data

def test_server_api_transactions(server_setup):
    with urllib.request.urlopen(f"{server_setup}/api/transactions") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert len(data) >= 20

def test_server_api_subscriptions(server_setup):
    with urllib.request.urlopen(f"{server_setup}/api/subscriptions") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert len(data) >= 1

def test_server_api_anomalies(server_setup):
    with urllib.request.urlopen(f"{server_setup}/api/anomalies") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert isinstance(data, list)
