import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import argparse
import os
from colorama import init, Fore, Style
from src.db import Database
from src.importer import StatementImporter
from src.categorizer import TransactionCategorizer
from src.analytics import AnalyticsEngine
from src.reporter import FinancialReporter
from src.server import run_server

init(autoreset=True)

def print_banner():
    banner = f"""
{Fore.GREEN}=======================================================
  AI Finance Tracker (AFT) — 100% Local-First Finance
  Built by Vecesta.co
======================================================={Style.RESET_ALL}"""
    print(banner)

def main():
    parser = argparse.ArgumentParser(
        prog="ai-finance-tracker",
        description="100% local-first personal finance tracker with dual-stage AI categorization."
    )
    parser.add_argument("--db", default=os.getenv("DATABASE_PATH", "finance.db"), help="Path to SQLite database")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Import
    p_imp = subparsers.add_parser("import", help="Import transactions from CSV statement")
    p_imp.add_argument("file", help="Path to CSV bank statement")
    p_imp.add_argument("--account", default="Checking", help="Account name")
    p_imp.add_argument("--auto-categorize", action="store_true", default=True, help="Automatically categorize on import")

    # 2. Categorize
    subparsers.add_parser("categorize", help="Re-categorize all uncategorized transactions")

    # 3. List
    p_list = subparsers.add_parser("list", help="List recent transactions")
    p_list.add_argument("--limit", type=int, default=20, help="Number of transactions to display")

    # 4. Summary
    subparsers.add_parser("summary", help="Show cashflow summary and category breakdown")

    # 5. Subscriptions
    subparsers.add_parser("subscriptions", help="Detect active recurring subscriptions")

    # 6. Anomalies
    subparsers.add_parser("anomalies", help="Detect spending anomalies and outliers")

    # 7. Serve
    p_serve = subparsers.add_parser("serve", help="Launch local web dashboard")
    p_serve.add_argument("--port", type=int, default=5000, help="Port for web dashboard")
    p_serve.add_argument("--host", default="127.0.0.1", help="Host address")

    args = parser.parse_args()
    db = Database(args.db)

    if args.command == "import":
        print_banner()
        print(f"{Fore.YELLOW}[*] Importing transactions from {args.file}...{Style.RESET_ALL}")
        txs = StatementImporter.import_csv(args.file, default_account=args.account)
        if args.auto_categorize:
            print(f"{Fore.YELLOW}[*] Running dual-stage categorization...{Style.RESET_ALL}")
            categorizer = TransactionCategorizer()
            txs = categorizer.categorize_batch(txs)
        count = db.insert_transactions(txs)
        print(f"{Fore.GREEN}[✓] Successfully imported and categorized {count} transactions into {args.db}!{Style.RESET_ALL}")

    elif args.command == "categorize":
        print_banner()
        print(f"{Fore.YELLOW}[*] Categorizing uncategorized transactions...{Style.RESET_ALL}")
        categorizer = TransactionCategorizer()
        txs = db.get_all_transactions()
        updated = 0
        for t in txs:
            if t.category == "Uncategorized" or t.confidence < 0.5:
                cat, conf = categorizer.categorize(t)
                db.update_transaction_category(t.id, cat, conf)
                updated += 1
        print(f"{Fore.GREEN}[✓] Categorization complete. Updated {updated} transactions.{Style.RESET_ALL}")

    elif args.command == "list":
        print_banner()
        txs = db.get_all_transactions()[:args.limit]
        if not txs:
            print(f"{Fore.CYAN}No transactions found in database. Run 'aft import <file.csv>' first.{Style.RESET_ALL}")
            return
        print(f"{'Date':<12} {'Payee':<24} {'Category':<16} {'Amount':>10}")
        print("-" * 65)
        for t in txs:
            color = Fore.RED if t.amount < 0 else Fore.GREEN
            sign = "-$" if t.amount < 0 else "+$"
            print(f"{t.date:<12} {t.payee[:22]:<24} {t.category:<16} {color}{sign}{abs(t.amount):>8.2f}{Style.RESET_ALL}")

    elif args.command == "summary":
        print_banner()
        txs = db.get_all_transactions()
        summary = AnalyticsEngine.summarize_cashflow(txs)
        print(FinancialReporter.format_terminal_summary(summary))

    elif args.command == "subscriptions":
        print_banner()
        print(f"{Fore.YELLOW}[*] Analyzing transaction intervals for recurring patterns...{Style.RESET_ALL}\n")
        txs = db.get_all_transactions()
        subs = AnalyticsEngine.detect_subscriptions(txs)
        print(FinancialReporter.format_subscriptions_table(subs))

    elif args.command == "anomalies":
        print_banner()
        print(f"{Fore.YELLOW}[*] Computing statistical Median Absolute Deviation per category...{Style.RESET_ALL}\n")
        txs = db.get_all_transactions()
        anomalies = AnalyticsEngine.detect_anomalies(txs)
        print(FinancialReporter.format_anomalies_table(anomalies))

    elif args.command == "serve":
        print_banner()
        run_server(db=db, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
