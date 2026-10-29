from typing import List
from src.models import CashflowSummary, Subscription, Anomaly, Transaction

class FinancialReporter:
    """Formats financial summaries into clean Markdown and terminal ASCII text."""

    @classmethod
    def format_terminal_summary(cls, summary: CashflowSummary) -> str:
        lines = [
            "-------------------------------------------------------",
            f" Total Transactions Processed: {summary.transaction_count}",
            f" Total Income:                 +${summary.total_income:,.2f}",
            f" Total Expenses:               -${summary.total_expenses:,.2f}",
            f" Net Savings:                  ${summary.net_savings:,.2f}",
            f" Savings Rate:                 {summary.savings_rate:.1f}%",
            "-------------------------------------------------------",
            " Top Spending Categories:",
        ]
        for cat, amt in list(summary.category_breakdown.items())[:6]:
            pct = (amt / summary.total_expenses * 100) if summary.total_expenses > 0 else 0
            lines.append(f"   • {cat:<18} ${amt:>9,.2f}  ({pct:>4.1f}%)")
        lines.append("-------------------------------------------------------")
        return "\n".join(lines)

    @classmethod
    def format_subscriptions_table(cls, subs: List[Subscription]) -> str:
        if not subs:
            return "No recurring subscriptions detected."
        lines = [
            f"{'Merchant':<22} {'Amount':<10} {'Cadence':<10} {'Annual Cost':<12} {'Last Billed'}",
            "-" * 65
        ]
        for s in subs:
            lines.append(
                f"{s.payee[:20]:<22} ${s.amount:<9.2f} {s.cadence:<10} ${s.annual_cost:<11.2f} {s.last_date}"
            )
        return "\n".join(lines)

    @classmethod
    def format_anomalies_table(cls, anomalies: List[Anomaly]) -> str:
        if not anomalies:
            return "No statistical anomalies detected. Spending is within normal variance."
        lines = [
            f"{'Date':<12} {'Payee':<20} {'Amount':<10} {'Category':<15} {'Deviation Score'}",
            "-" * 70
        ]
        for a in anomalies:
            lines.append(
                f"{a.date:<12} {a.payee[:18]:<20} ${abs(a.amount):<9.2f} {a.category:<15} {a.score:.1f}x MAD"
            )
        return "\n".join(lines)
