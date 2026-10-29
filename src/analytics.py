from collections import defaultdict
from datetime import datetime
import numpy as np
from typing import List, Dict
from src.models import Transaction, Subscription, Anomaly, CashflowSummary

class AnalyticsEngine:
    """Financial analytics: Subscription discovery, anomaly detection, and cashflow modeling."""

    @classmethod
    def parse_date(cls, date_str: str) -> datetime:
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return datetime.now()

    @classmethod
    def detect_subscriptions(cls, transactions: List[Transaction]) -> List[Subscription]:
        """Cluster debit transactions by normalized payee and detect recurring intervals."""
        clusters = defaultdict(list)
        for t in transactions:
            if t.amount < 0:  # Debits only
                key = t.payee.lower().strip()
                clusters[key].append(t)

        subs: List[Subscription] = []
        for payee, txs in clusters.items():
            if len(txs) < 2:
                continue

            # Sort chronologically
            sorted_txs = sorted(txs, key=lambda x: cls.parse_date(x.date))
            dates = [cls.parse_date(x.date) for x in sorted_txs]
            deltas = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
            median_delta = float(np.median(deltas))

            amounts = [abs(x.amount) for x in sorted_txs]
            avg_amount = float(np.mean(amounts))
            amount_std = float(np.std(amounts))

            # Variance ratio check
            if avg_amount > 0 and (amount_std / avg_amount) > 0.20:
                continue  # Amounts fluctuate too much for a fixed subscription

            cadence = None
            annual_multiplier = 0
            if 25 <= median_delta <= 35:
                cadence = "Monthly"
                annual_multiplier = 12
            elif 6 <= median_delta <= 8:
                cadence = "Weekly"
                annual_multiplier = 52
            elif 350 <= median_delta <= 380:
                cadence = "Annual"
                annual_multiplier = 1

            if cadence:
                subs.append(
                    Subscription(
                        payee=sorted_txs[-1].payee,
                        amount=round(avg_amount, 2),
                        cadence=cadence,
                        transaction_count=len(sorted_txs),
                        last_date=sorted_txs[-1].date,
                        annual_cost=round(avg_amount * annual_multiplier, 2),
                    )
                )

        subs.sort(key=lambda s: s.annual_cost, reverse=True)
        return subs

    @classmethod
    def detect_anomalies(cls, transactions: List[Transaction], threshold: float = 2.5) -> List[Anomaly]:
        """Detect spending anomalies using Median Absolute Deviation (MAD) partitioned by category."""
        category_map = defaultdict(list)
        for t in transactions:
            if t.amount < 0:  # Expenses only
                category_map[t.category].append(t)

        anomalies: List[Anomaly] = []
        for cat, txs in category_map.items():
            if len(txs) < 4:
                continue

            amounts = np.array([abs(x.amount) for x in txs])
            med = np.median(amounts)
            mad = np.median(np.abs(amounts - med))

            if mad == 0:
                mad = np.std(amounts)
            if mad == 0:
                continue

            for t in txs:
                score = (abs(t.amount) - med) / mad
                if score >= threshold:
                    anomalies.append(
                        Anomaly(
                            transaction_id=t.id or 0,
                            date=t.date,
                            payee=t.payee,
                            amount=t.amount,
                            category=cat,
                            reason=f"Charge of ${abs(t.amount):.2f} exceeds {cat} median (${med:.2f}) by {score:.1f}x MAD",
                            score=round(score, 2),
                        )
                    )

        anomalies.sort(key=lambda a: a.score, reverse=True)
        return anomalies

    @classmethod
    def summarize_cashflow(cls, transactions: List[Transaction]) -> CashflowSummary:
        """Calculate total income, expenses, savings rate, and category breakdowns."""
        total_income = 0.0
        total_expenses = 0.0
        breakdown = defaultdict(float)

        for t in transactions:
            if t.amount > 0:
                total_income += t.amount
            else:
                exp = abs(t.amount)
                total_expenses += exp
                breakdown[t.category] += exp

        net_savings = total_income - total_expenses
        savings_rate = (net_savings / total_income * 100.0) if total_income > 0 else 0.0

        return CashflowSummary(
            total_income=round(total_income, 2),
            total_expenses=round(total_expenses, 2),
            net_savings=round(net_savings, 2),
            savings_rate=round(savings_rate, 1),
            category_breakdown={k: round(v, 2) for k, v in sorted(breakdown.items(), key=lambda x: x[1], reverse=True)},
            transaction_count=len(transactions),
        )
