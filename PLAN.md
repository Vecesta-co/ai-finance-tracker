# PLAN.md — ai-finance-tracker

## 1. Executive Summary

`ai-finance-tracker` is a 100% local-first, privacy-preserving personal finance tracker and intelligent transaction categorization engine built by Vecesta.co. It provides automated CSV bank statement ingestion, dual deterministic and zero-shot AI transaction categorization, recurring subscription detection, statistical anomaly detection, and cashflow forecasting. It runs entirely on local SQLite with zero bank credential storage and zero telemetry.

---

## 2. Competitive Landscape & Reference Analysis

- **Reference**: `actualbudget/actual` (MIT License).
- **Existing Limitations**:
  - Actual Budget and classic finance trackers rely on exact regex string matching for rule assignments, requiring hundreds of manual rules for messy real-world card statements (e.g. `TST* BLUE BOTTLE COFFEE #12`, `AMZN MKTP US*8A29`).
  - Mainstream commercial apps (Mint, Monarch, Copilot) mandate cloud syncing of financial credentials through aggregators like Plaid or Yodlee, exposing private banking data.
  - Most open-source budgeting software lacks statistical anomaly detection (catching double charges or unusual spikes) and automatic recurring subscription discovery.
- **How We Are Different & More Capable**:
  1. **Dual-Stage Categorization Engine**: Combines a high-throughput deterministic rule bank with a contextual zero-shot AI classifier (Ollama / Gemini / OpenAI / deterministic fallback), achieving >95% auto-categorization accuracy.
  2. **Zero Credential Requirement**: Operates strictly on exported CSV/OFX statements — no bank passwords, API tokens, or cloud sync required.
  3. **Automated Recurring Subscription Discovery**: Calculates inter-transaction intervals, day-of-month alignment, and amount variance to identify active subscriptions and annual costs.
  4. **Statistical Spending Anomaly Detection**: Employs Median Absolute Deviation (MAD) to detect duplicate charges, merchant overbills, and category spending surges.
  5. **Zero-Lockin SQLite Foundation**: Standard SQLite database with schema versioning, easy backups, and JSON/CSV data export.

---

## 3. Architecture & Tech Stack

```
           Bank Statement Export (.csv / .ofx)
                          │
                          ▼
             ┌─────────────────────────┐
             │ Smart Statement Importer│
             │ - Column auto-mapping   │
             │ - Date & amount parser  │
             └────────────┬────────────┘
                          │
                          ▼
             ┌─────────────────────────┐
             │ Categorization Engine   │
             │ Stage 1: Fast Rule Bank │
             │ Stage 2: AI Zero-Shot   │
             └────────────┬────────────┘
                          │
                          ▼
             ┌─────────────────────────┐
             │ SQLite Local Repository │
             │ - Transactions, Budgets │
             │ - Categories, Metadata  │
             └────────────┬────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
┌─────────────────┐ ┌───────────┐ ┌─────────────────┐
│Analytics Engine │ │Terminal   │ │Embedded Web     │
│- Subscriptions  │ │CLI        │ │Dashboard & API  │
│- Anomalies      │ │(Rich Text)│ │(REST / SQLite)  │
│- Cashflow Forec.│ └───────────┘ └─────────────────┘
└─────────────────┘
```

- **Runtime**: Python 3.10+
- **Database**: SQLite 3 with WAL mode
- **Libraries**: `pydantic` (schemas), `pandas`/`numpy` (data analysis), `pytest` (testing)
- **Target Coverage**: >85%

---

## 4. File Structure

```
ai-finance-tracker/
├── PLAN.md
├── DEVLOG.md
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── Dockerfile
├── pyproject.toml
├── .gitignore
├── .env.example
├── .github/
│   ├── workflows/ci.yml
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── fixtures/
│   └── sample_bank_statement.csv
├── src/
│   ├── __init__.py
│   ├── models.py
│   ├── db.py
│   ├── importer.py
│   ├── categorizer.py
│   ├── analytics.py
│   ├── reporter.py
│   ├── server.py
│   └── cli.py
└── tests/
    ├── __init__.py
    ├── test_analytics.py
    ├── test_categorizer.py
    ├── test_cli.py
    ├── test_db.py
    ├── test_importer.py
    ├── test_models.py
    └── test_server.py
```
