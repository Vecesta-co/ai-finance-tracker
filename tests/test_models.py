import pytest
from src.models import Transaction, Category, Subscription, Anomaly, CashflowSummary

def test_transaction_model():
    t = Transaction(
        date="2026-01-01",
        payee="Coffee Shop",
        raw_description="SQ *COFFEE SHOP",
        amount=-4.50,
        category="Dining",
        confidence=0.95
    )
    assert t.amount == -4.50
    assert t.category == "Dining"
    assert t.confidence == 0.95

def test_subscription_model():
    s = Subscription(
        payee="Netflix",
        amount=19.99,
        cadence="Monthly",
        transaction_count=3,
        last_date="2026-03-08",
        annual_cost=239.88
    )
    assert s.annual_cost == 239.88
    assert s.cadence == "Monthly"

def test_cashflow_summary_model():
    cs = CashflowSummary(
        total_income=5000.0,
        total_expenses=3000.0,
        net_savings=2000.0,
        savings_rate=40.0,
        category_breakdown={"Housing": 1500.0, "Food": 500.0},
        transaction_count=10
    )
    assert cs.net_savings == 2000.0
    assert cs.savings_rate == 40.0
