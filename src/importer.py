import csv
import re
from typing import List, Optional
from src.models import Transaction

class StatementImporter:
    """Smart CSV bank statement parser with column autodetection and normalization."""

    DATE_ALIASES = ("date", "posting date", "trans date", "transaction date", "time")
    PAYEE_ALIASES = ("payee", "description", "merchant", "details", "narrative", "name")
    AMOUNT_ALIASES = ("amount", "trans amount", "transaction amount", "total")
    DEBIT_ALIASES = ("debit", "withdrawal", "spent")
    CREDIT_ALIASES = ("credit", "deposit", "earned")

    @classmethod
    def clean_amount(cls, val: str) -> float:
        """Parse messy amount strings like '$1,234.56', '(45.00)', or '-12.50'."""
        val = val.strip()
        if not val:
            return 0.0
        # Parentheses denote negative
        is_negative = False
        if val.startswith("(") and val.endswith(")"):
            is_negative = True
            val = val[1:-1]
        val = re.sub(r"[^\d.-]", "", val)
        try:
            num = float(val)
            return -abs(num) if is_negative else num
        except ValueError:
            return 0.0

    @classmethod
    def import_csv(cls, file_path: str, default_account: str = "Checking") -> List[Transaction]:
        """Read CSV statement and return normalized Transaction objects."""
        transactions: List[Transaction] = []

        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return []

            field_map = {fn.strip().lower(): fn for fn in reader.fieldnames}

            # Map date column
            date_col = next((field_map[k] for k in cls.DATE_ALIASES if k in field_map), None)
            payee_col = next((field_map[k] for k in cls.PAYEE_ALIASES if k in field_map), None)
            amount_col = next((field_map[k] for k in cls.AMOUNT_ALIASES if k in field_map), None)
            debit_col = next((field_map[k] for k in cls.DEBIT_ALIASES if k in field_map), None)
            credit_col = next((field_map[k] for k in cls.CREDIT_ALIASES if k in field_map), None)

            if not date_col or not payee_col or (not amount_col and not debit_col):
                raise ValueError("Could not automatically map essential columns (Date, Payee, Amount/Debit).")

            for row in reader:
                raw_date = row.get(date_col, "").strip()
                raw_desc = row.get(payee_col, "").strip()
                if not raw_date or not raw_desc:
                    continue

                if amount_col:
                    amt = cls.clean_amount(row.get(amount_col, "0"))
                else:
                    debit = abs(cls.clean_amount(row.get(debit_col, "0")))
                    credit = abs(cls.clean_amount(row.get(credit_col, "0")))
                    amt = credit - debit

                # Payee cleaning (strip terminal IDs, prefixes like SQ *, TST *)
                clean_payee = re.sub(r"^(sq\s*\*|tst\s*\*|paypal\s*\*|amzn\s*mktp\s*)", "", raw_desc, flags=re.I).strip()

                transactions.append(
                    Transaction(
                        date=raw_date,
                        payee=clean_payee or raw_desc,
                        raw_description=raw_desc,
                        amount=amt,
                        account=default_account,
                    )
                )

        return transactions
