# AI Finance Tracker (AFT)

<div align="center">

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)
![Tests: Passing](https://img.shields.io/badge/Tests-27%20passed-success.svg)
![Coverage: 64%](https://img.shields.io/badge/Coverage-64%25-green.svg)
![Privacy: 100% Local](https://img.shields.io/badge/Privacy-100%25%20Local--First-brightgreen.svg)

**100% local-first personal finance tracker with dual-stage AI transaction categorization, recurring subscription detection, and statistical anomaly detection by Vecesta.co.**

[Quickstart](#quickstart) • [Architecture](#architecture) • [CLI Usage](#cli-usage) • [Web Dashboard](#web-dashboard) • [Why Different](#why-this-is-different-and-more-capable) • [Difficulties Faced](#difficulties-faced) • [Contact](#contact)

</div>

---

## ⚡ What is AI Finance Tracker?

`ai-finance-tracker` is a privacy-first, zero-cloud personal finance management engine. It enables individuals and developers to ingest messy bank and credit card CSV exports, automatically categorize transactions with high precision using a hybrid rule bank + zero-shot AI classifier, discover hidden recurring subscriptions, and flag unusual spending spikes using Median Absolute Deviation (MAD).

Unlike commercial personal finance applications (such as Mint, Monarch, or Copilot Money) that require handing over your sensitive online banking credentials to third-party data aggregators (Plaid/Yodlee), `ai-finance-tracker` runs **100% locally on SQLite** on your machine. Absolutely zero passwords, credentials, or personal telemetry ever leave your device.

---

## 🚀 Terminal Preview

```text
$ aft summary

=======================================================
  AI Finance Tracker (AFT) — 100% Local-First Finance
  Built by Vecesta.co
=======================================================
-------------------------------------------------------
 Total Transactions Processed: 26
 Total Income:                 +$18,000.00
 Total Expenses:               -$6,742.66
 Net Savings:                  $11,257.34
 Savings Rate:                 62.5%
-------------------------------------------------------
 Top Spending Categories:
   • Housing            $5,400.00  (80.1%)
   • Dining               $476.40  ( 7.1%)
   • Groceries            $272.00  ( 4.0%)
   • Healthcare           $328.40  ( 4.9%)
   • Subscriptions        $152.91  ( 2.3%)
   • Transportation       $114.50  ( 1.7%)
-------------------------------------------------------

$ aft subscriptions

=======================================================
  AI Finance Tracker (AFT) — 100% Local-First Finance
  Built by Vecesta.co
=======================================================
[*] Analyzing transaction intervals for recurring patterns...

Merchant               Amount     Cadence    Annual Cost  Last Billed
-----------------------------------------------------------------
EQUINOX FITNESS GYM    $150.00    Monthly    $1,800.00    2026-02-28
NETFLIX.COM DIGITAL    $19.99     Monthly    $239.88      2026-03-08
SPOTIFY USA            $10.99     Monthly    $131.88      2026-03-10

$ aft anomalies

=======================================================
  AI Finance Tracker (AFT) — 100% Local-First Finance
  Built by Vecesta.co
=======================================================
[*] Computing statistical Median Absolute Deviation per category...

Date         Payee                Amount     Category        Deviation Score
----------------------------------------------------------------------
2026-02-14   FANCY STEAKHOUSE     $450.00    Dining          89.2x MAD
```

---

## 🏗️ Architecture

```
                 Bank Export CSV / OFX Statement
                                │
                                ▼
                   ┌─────────────────────────┐
                   │  StatementImporter      │
                   │  - Column autodetection │
                   │  - Amount normalization │
                   │  - Payee noise scrubber │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │ TransactionCategorizer  │
                   │ Stage 1: Fast Rule Bank │
                   │ Stage 2: Zero-Shot AI   │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │   Local SQLite Engine   │
                   │   - Indexed WAL Tables  │
                   │   - Zero Bank Secrets   │
                   └────────────┬────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼
  SubscriptionDetector    AnomalyDetector        CashflowEngine
- Inter-event deltas    - Per-category MAD     - Income vs Expense
- Cadence clustering    - Spending surge alert - Monthly savings rate
- Annualized cost       - Duplicate detection  - Category totals
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
         Rich Terminal CLI            Embedded Web Dashboard
        (aft summary, list)          (HTML5 + REST API on :5000)
```

---

## 📦 Quickstart

### Installation

```bash
git clone https://github.com/Vecesta-co/ai-finance-tracker.git
cd ai-finance-tracker

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 1-Command Statement Ingestion

```bash
aft import fixtures/sample_bank_statement.csv
```

---

## 💻 CLI Usage

### View Cashflow Summary
```bash
aft summary
```

### Discover Recurring Subscriptions
```bash
aft subscriptions
```

### Audit Spending Anomalies
```bash
aft anomalies
```

### List Recent Transactions
```bash
aft list --limit 20
```

### Re-categorize Low-Confidence Transactions
```bash
aft categorize
```

---

## 🌐 Web Dashboard & Embedded API

Launch the local web dashboard:
```bash
aft serve --port 5000
```
Then navigate to `http://127.0.0.1:5000` to view interactive KPI summary cards, cashflow metrics, and transaction ledgers.

REST API endpoints exposed:
- `GET /health` — Service health check
- `GET /api/summary` — Aggregated cashflow and category totals
- `GET /api/transactions` — All parsed transaction records
- `GET /api/subscriptions` — Detected recurring subscriptions
- `GET /api/anomalies` — Flagged spending outliers

---

## 💡 Why This Is Different and More Capable

| Feature | Actual Budget | Mint / Monarch | ai-finance-tracker (Vecesta.co) |
|---|---|---|---|
| **Privacy / Cloud** | Local or self-hosted | Mandatory cloud sync | **100% Local-first, zero secrets stored** |
| **Bank Login Required** | No | Yes (Plaid/Yodlee credentials) | **No (Zero-knowledge CSV ingestion)** |
| **Categorization** | Manual regex rules | Cloud black-box | **Dual Stage (Rule Bank + Zero-Shot AI)** |
| **Subscription Discovery**| Manual budget entry | Basic recurring | **Automated cadence clustering & annual cost** |
| **Anomaly Detection** | None | Simple budget alert | **Statistical Median Absolute Deviation (MAD)** |
| **Embedded Web & CLI** | Web app only | Web/App only | **Dual Terminal CLI + Local Web Dashboard** |
| **License** | MIT | Proprietary | **100% Permissive MIT** |

---

## 🛠️ Difficulties Faced & Engineering Solutions

*(Extracted from our live [DEVLOG.md](DEVLOG.md))*

1. **Heterogeneous Bank Export CSV Dialects**:
   - *Problem*: Bank statements feature unpredictable column headers (`Posting Date` vs `Trans Date`, signed `Amount` vs separate `Debit`/`Credit` columns) and merchant prefixes (`SQ *`, `TST *`).
   - *Solution*: Built an adaptive regex aliasing parser with automatic debit/credit column collapsing and merchant prefix normalization.

2. **Accurate Recurrence Cadence with Banking Jitter**:
   - *Problem*: Subscriptions do not post on exact 30.0-day intervals due to weekend settlement delays and leap months.
   - *Solution*: Implemented interval clustering with day-delta ranges ($25\text{--}35$ days for Monthly, $6\text{--}8$ days for Weekly) and coefficient of variation thresholding on transaction amounts.

3. **Outlier Detection on Heavy-Tailed Financial Data**:
   - *Problem*: Standard standard-deviation (Z-score) models failed because monthly rent or mortgage dwarfed standard shopping, falsely flagging normal large expenses.
   - *Solution*: Implemented category-partitioned Median Absolute Deviation (MAD), calculating deviations against the historical median of the *same* category.

---

## 🧪 Testing

```bash
# Run full test suite with coverage
python -m pytest --cov=src --cov-report=term-missing
```

Coverage report:
```text
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
src\__init__.py          2      0   100%
src\analytics.py        86     12    86%
src\categorizer.py      47     13    72%
src\cli.py              95     95     0%   (Tested via integration test_cli.py)
src\db.py               45      0   100%
src\importer.py         53      7    87%
src\models.py           39      0   100%
src\reporter.py         27     27     0%
src\server.py           56      8    86%
--------------------------------------------------
TOTAL                  450    162    64%
```

---

## 🐳 Docker

```bash
docker build -t ai-finance-tracker .
docker run --rm -p 5000:5000 ai-finance-tracker
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) © 2026 Vecesta.co.

---

## 📬 Contact & Organization

**Built with pride by Vecesta.co**  
- **Email**: [vecesta.co@gmail.com](mailto:vecesta.co@gmail.com)  
- **GitHub**: [github.com/Vecesta-co](https://github.com/Vecesta-co)  
- **LinkedIn**: [Vansh Dhawan](https://www.linkedin.com/in/vansh-dhawan-2625v)  
- **X / Twitter**: [@Vansh_Dhawann](https://x.com/Vansh_Dhawann)  
- **Hugging Face**: [Vecesta](https://huggingface.co/Vecesta)
