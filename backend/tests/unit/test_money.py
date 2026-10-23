from decimal import Decimal

import pytest

from app.core.money import percent_of, to_money


def test_rounds_half_up_not_bankers():
    assert to_money("2.345") == Decimal("2.35")
    assert to_money("2.355") == Decimal("2.36")


def test_rejects_float():
    with pytest.raises(TypeError):
        to_money(0.1)  # type: ignore[arg-type]


def test_percent_of():
    assert percent_of(Decimal("100000"), Decimal("2.5")) == Decimal("2500.00")
    assert percent_of(Decimal("333.33"), Decimal("1.5")) == Decimal("5.00")
