"""Single source of truth for monetary arithmetic.

Rules: never use float; quantize to 2 dp with ROUND_HALF_UP; store as NUMERIC(14,2).
"""

from decimal import ROUND_HALF_UP, Decimal

MONEY_QUANTUM = Decimal("0.01")
ZERO = Decimal("0.00")


def to_money(value: Decimal | int | str) -> Decimal:
    if isinstance(value, float):
        raise TypeError("float is not allowed for money; use Decimal, int or str")
    return Decimal(value).quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


def percent_of(amount: Decimal, rate_percent: Decimal) -> Decimal:
    """amount * rate_percent / 100, rounded once at the end."""
    return to_money(amount * rate_percent / Decimal(100))
