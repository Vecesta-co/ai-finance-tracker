import pytest
from src.categorizer import TransactionCategorizer
from src.models import Transaction

@pytest.fixture
def categorizer():
    return TransactionCategorizer(mode="heuristic")

def test_categorize_rules(categorizer):
    t_grocery = Transaction(date="2026-01-01", payee="Trader Joe's", raw_description="TRADER JOES #102", amount=-50.0)
    cat, conf = categorizer.categorize(t_grocery)
    assert cat == "Groceries"
    assert conf >= 0.9

    t_sub = Transaction(date="2026-01-01", payee="Netflix.com", raw_description="NETFLIX DIGITAL", amount=-19.99)
    cat, conf = categorizer.categorize(t_sub)
    assert cat == "Subscriptions"

    t_payroll = Transaction(date="2026-01-01", payee="Payroll Inc", raw_description="EMPLOYER DIRECT DEP", amount=4000.0)
    cat, conf = categorizer.categorize(t_payroll)
    assert cat == "Income"

    t_uber = Transaction(date="2026-01-01", payee="Uber", raw_description="UBER TRIP", amount=-22.0)
    cat, conf = categorizer.categorize(t_uber)
    assert cat == "Transportation"

def test_categorize_ai_fallback(categorizer):
    t_unknown = Transaction(date="2026-01-01", payee="Random Unlisted Merchant XYZ", raw_description="XYZ123", amount=-8.50)
    cat, conf = categorizer.categorize(t_unknown)
    assert cat in ("Dining", "Shopping", "Housing")
    assert conf > 0.0

def test_categorize_batch(categorizer):
    txs = [
        Transaction(date="2026-01-01", payee="Chevron", raw_description="CHEVRON GAS", amount=-40.0),
        Transaction(date="2026-01-02", payee="Whole Foods", raw_description="WHOLE FOODS", amount=-60.0),
    ]
    categorizer.categorize_batch(txs)
    assert txs[0].category == "Transportation"
    assert txs[1].category == "Groceries"
