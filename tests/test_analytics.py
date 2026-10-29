import pytest
from src.importer import StatementImporter
from src.categorizer import TransactionCategorizer
from src.analytics import AnalyticsEngine

@pytest.fixture
def statement_data():
    txs = StatementImporter.import_csv("fixtures/sample_bank_statement.csv")
    categorizer = TransactionCategorizer()
    return categorizer.categorize_batch(txs)

def test_detect_subscriptions(statement_data):
    subs = AnalyticsEngine.detect_subscriptions(statement_data)
    payees = [s.payee.lower() for s in subs]
    assert any("netflix" in p for p in payees)
    assert any("spotify" in p for p in payees)
    
    netflix_sub = next(s for s in subs if "netflix" in s.payee.lower())
    assert netflix_sub.cadence == "Monthly"
    assert netflix_sub.amount == 19.99
    assert netflix_sub.annual_cost == round(19.99 * 12, 2)

def test_detect_anomalies(statement_data):
    anomalies = AnalyticsEngine.detect_anomalies(statement_data, threshold=2.0)
    # The $450 fancy steakhouse dinner should be flagged as anomaly in Dining
    assert any("STEAKHOUSE" in a.payee or a.amount == -450.0 for a in anomalies)

def test_summarize_cashflow(statement_data):
    summary = AnalyticsEngine.summarize_cashflow(statement_data)
    assert summary.total_income > 10000.0
    assert summary.total_expenses > 5000.0
    assert summary.net_savings > 0
    assert summary.savings_rate > 0
    assert "Housing" in summary.category_breakdown
    assert "Groceries" in summary.category_breakdown
