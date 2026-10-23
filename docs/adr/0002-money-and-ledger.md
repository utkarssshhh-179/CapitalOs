# ADR 0002: Money handling and append-only ledger
Status: accepted

- Money is `Decimal` in Python and `NUMERIC(14,2)` in PostgreSQL. Floats are rejected.
- Rounding: ROUND_HALF_UP to 2dp, applied once at the end of a calculation (`app/core/money.py`).
- Payments, accruals and penalties are immutable ledger entries. Balances are derived.
  Corrections are reversal entries, never updates or deletes.
