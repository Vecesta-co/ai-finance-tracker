# DEVLOG.md — ai-finance-tracker

## Engineering Log & Challenges Solved

### Milestone 1: Core Architecture & Privacy Foundations
- **Date**: 2026-10-29
- **Goal**: Build a privacy-first, local-first finance manager with automated ingestion and multi-model categorization.
- **Key Tenet**: Zero transmission of raw bank credentials or account tokens. All data lives in a local SQLite file (`finance.db`).

---

### Obstacle 1: Ambiguous Bank CSV Statement Formats
- **Problem**: Different banks format statements inconsistently (e.g., Chase has `Posting Date`, `Description`, `Amount` where debits are negative; BoA has separate `Debit` and `Credit` columns; Wells Fargo uses `Transaction Date`).
- **Solution**: Built an adaptive `StatementImporter` with flexible regex-based header aliasing (`DATE_ALIASES`, `AMOUNT_ALIASES`, `PAYEE_ALIASES`) and sign normalization that handles single signed amount columns as well as separate debit/credit columns.

---

### Obstacle 2: Subscription Interval and Renewal Detection
- **Problem**: Detecting subscriptions purely by identical merchant names fails when billing amounts fluctuate slightly (e.g., utility bills or currency exchange conversions) or when dates vary by 1-3 days due to weekend banking settlement delays.
- **Solution**: Engineered a robust subscription clustering algorithm in `src/analytics.py` that calculates the median recurrence delta in days ($\approx 28\text{--}31$ days for monthly, $\approx 360\text{--}370$ days for annual) and permits an amount variance threshold ($\le 15\%$).

---

### Obstacle 3: Real-Time Anomaly Sensitivity
- **Problem**: Standard Z-score anomaly detection fails on financial transaction distributions because spending is heavily right-skewed with long tails (e.g., monthly rent looks like an anomaly compared to $4 coffees).
- **Solution**: Applied category-partitioned Median Absolute Deviation (MAD), computing outliers relative to historical medians within the *same* category rather than across the global statement.
