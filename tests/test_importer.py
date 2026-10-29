import pytest
from src.importer import StatementImporter

def test_clean_amount():
    assert StatementImporter.clean_amount("45.50") == 45.50
    assert StatementImporter.clean_amount("-12.30") == -12.30
    assert StatementImporter.clean_amount("$1,234.56") == 1234.56
    assert StatementImporter.clean_amount("(75.00)") == -75.00
    assert StatementImporter.clean_amount("") == 0.0

def test_import_sample_csv():
    txs = StatementImporter.import_csv("fixtures/sample_bank_statement.csv")
    assert len(txs) >= 20
    assert any(t.amount > 0 for t in txs)  # Has payroll
    assert any(t.amount < 0 for t in txs)  # Has debits

    # Check payee cleaning prefix removal
    blue_bottle = next(t for t in txs if "BLUE BOTTLE" in t.raw_description)
    assert not blue_bottle.payee.startswith("SQ *")

def test_import_invalid_csv_raises(tmp_path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("ColA,ColB\n1,2\n")
    with pytest.raises(ValueError):
        StatementImporter.import_csv(str(bad_csv))
