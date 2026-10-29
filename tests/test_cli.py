import subprocess
import sys
import os
import tempfile
import pytest

@pytest.fixture
def cli_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)

def test_cli_help():
    res = subprocess.run([sys.executable, "-m", "src.cli", "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "ai-finance-tracker" in res.stdout
    assert "import" in res.stdout
    assert "summary" in res.stdout

def test_cli_import_and_summary(cli_db):
    res_imp = subprocess.run(
        [sys.executable, "-m", "src.cli", "--db", cli_db, "import", "fixtures/sample_bank_statement.csv"],
        capture_output=True,
        text=True
    )
    assert res_imp.returncode == 0
    assert "Successfully imported" in res_imp.stdout

    res_sum = subprocess.run(
        [sys.executable, "-m", "src.cli", "--db", cli_db, "summary"],
        capture_output=True,
        text=True
    )
    assert res_sum.returncode == 0
    assert "Total Income" in res_sum.stdout
    assert "Total Expenses" in res_sum.stdout

def test_cli_list(cli_db):
    subprocess.run([sys.executable, "-m", "src.cli", "--db", cli_db, "import", "fixtures/sample_bank_statement.csv"])
    res = subprocess.run([sys.executable, "-m", "src.cli", "--db", cli_db, "list", "--limit", "5"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Date" in res.stdout

def test_cli_subscriptions(cli_db):
    subprocess.run([sys.executable, "-m", "src.cli", "--db", cli_db, "import", "fixtures/sample_bank_statement.csv"])
    res = subprocess.run([sys.executable, "-m", "src.cli", "--db", cli_db, "subscriptions"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Merchant" in res.stdout

def test_cli_anomalies(cli_db):
    subprocess.run([sys.executable, "-m", "src.cli", "--db", cli_db, "import", "fixtures/sample_bank_statement.csv"])
    res = subprocess.run([sys.executable, "-m", "src.cli", "--db", cli_db, "anomalies"], capture_output=True, text=True)
    assert res.returncode == 0
