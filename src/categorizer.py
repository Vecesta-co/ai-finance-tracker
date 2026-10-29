import re
import os
import requests
from typing import Tuple, List, Optional
from src.models import Transaction

class TransactionCategorizer:
    """Dual-stage transaction categorizer combining fast rule bank and zero-shot AI."""

    RULES = [
        # Income
        ("Income", [r"payroll", r"salary", r"direct dep", r"employer", r"stipend", r"bonus", r"dividend", r"interest paid"]),
        # Housing / Rent
        ("Housing", [r"rent", r"landlord", r"mortgage", r"hoa", r"property mgmt", r"apartments"]),
        # Groceries
        ("Groceries", [r"whole foods", r"trader joe", r"safeway", r"kroger", r"supermarket", r"costco", r"walmart grocery", r"target grocery", r"market", r"grocery", r"aldi"]),
        # Dining & Food
        ("Dining", [r"starbucks", r"blue bottle", r"chipotle", r"mcdonald", r"restaurant", r"cafe", r"coffee", r"doordash", r"uber eats", r"grubhub", r"burger", r"pizza", r"bakery", r"steakhouse", r"dinner", r"bistro", r"bar\b"]),
        # Subscriptions / Digital Services
        ("Subscriptions", [r"netflix", r"spotify", r"hulu", r"disney\+", r"apple\.com/bill", r"google\*youtube", r"prime video", r"github", r"openai", r"chatgpt", r"audible", r"patreon"]),
        # Transportation
        ("Transportation", [r"uber\s*trip", r"lyft", r"chevron", r"shell", r"gas station", r"transit", r"caltrain", r"metro", r"parking", r"exxon", r"bp\b"]),
        # Utilities
        ("Utilities", [r"electric", r"pg&e", r"water bill", r"coned", r"internet", r"comcast", r"xfinity", r"verizon", r"at&t", r"t-mobile"]),
        # Healthcare & Fitness
        ("Healthcare", [r"pharmacy", r"cvs", r"walgreens", r"doctor", r"hospital", r"dental", r"gym", r"fitness", r"equinox", r"planet fitness"]),
        # Shopping
        ("Shopping", [r"amazon", r"amzn", r"target", r"best buy", r"apple store", r"ikea", r"zara", r"nike", r"clothing"]),
    ]

    def __init__(self, mode: str = "heuristic", api_key: Optional[str] = None):
        self.mode = mode.lower()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

    def categorize_rule(self, text: str) -> Optional[Tuple[str, float]]:
        """Stage 1: Fast deterministic regex matching."""
        lower = text.lower()
        for cat, patterns in self.RULES:
            for pat in patterns:
                if re.search(pat, lower):
                    return cat, 0.95
        return None

    def categorize_ai(self, payee: str, amount: float) -> Tuple[str, float]:
        """Stage 2: Zero-shot AI categorization with local heuristic fallback."""
        if self.mode == "gemini" and self.api_key:
            try:
                endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                prompt = (
                    f"Categorize this bank transaction into exactly one of: [Groceries, Dining, Subscriptions, Transportation, Housing, Utilities, Healthcare, Shopping, Income, Other].\n"
                    f"Payee: {payee}, Amount: ${amount:.2f}\n"
                    f"Output ONLY the category name."
                )
                payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
                res = requests.post(endpoint, json=payload, timeout=10)
                if res.status_code == 200:
                    cat = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    return cat, 0.88
            except Exception:
                pass

        # Heuristic zero-shot fallback based on amount semantics
        if amount > 1000:
            return "Housing", 0.70
        elif amount > 0:
            return "Income", 0.85
        elif abs(amount) < 15:
            return "Dining", 0.65
        return "Shopping", 0.50

    def categorize(self, t: Transaction) -> Tuple[str, float]:
        """Execute two-stage categorization."""
        # Stage 1: Rule match on cleaned payee and raw description
        rule_match = self.categorize_rule(t.payee) or self.categorize_rule(t.raw_description)
        if rule_match:
            return rule_match

        # Stage 2: AI categorization
        return self.categorize_ai(t.payee, t.amount)

    def categorize_batch(self, transactions: List[Transaction]) -> List[Transaction]:
        """Categorize a list of transactions in-place."""
        for t in transactions:
            cat, conf = self.categorize(t)
            t.category = cat
            t.confidence = conf
        return transactions
