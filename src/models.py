from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from datetime import date

class Transaction(BaseModel):
    """Normalized personal finance transaction."""
    id: Optional[int] = None
    date: str
    payee: str
    raw_description: str
    amount: float  # Negative for expenses, positive for income
    category: str = "Uncategorized"
    confidence: float = 0.0
    account: str = "Checking"
    notes: Optional[str] = None

class Category(BaseModel):
    """Spending category definition."""
    name: str
    budget_monthly: float = 0.0
    icon: Optional[str] = None

class Subscription(BaseModel):
    """Detected recurring subscription."""
    payee: str
    amount: float
    cadence: str  # Monthly, Annual, Weekly
    transaction_count: int
    last_date: str
    annual_cost: float

class Anomaly(BaseModel):
    """Detected spending anomaly or outlier."""
    transaction_id: int
    date: str
    payee: str
    amount: float
    category: str
    reason: str
    score: float

class CashflowSummary(BaseModel):
    """Aggregated financial summary."""
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate: float
    category_breakdown: Dict[str, float]
    transaction_count: int
