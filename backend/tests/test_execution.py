"""Slippage / notional tests."""

from __future__ import annotations

from decimal import Decimal

import pytest

from condor.engine.execution import apply_slippage, notional

D = Decimal


def test_buy_pays_up() -> None:
    assert apply_slippage(D(100), "buy", D(5)) == D("100.05")


def test_sell_receives_less() -> None:
    assert apply_slippage(D(100), "sell", D(5)) == D("99.95")


def test_zero_slippage_is_identity() -> None:
    assert apply_slippage(D("123.45"), "buy", D(0)) == D("123.45")


def test_invalid_side() -> None:
    with pytest.raises(ValueError, match="invalid side"):
        apply_slippage(D(100), "hold", D(5))


def test_notional() -> None:
    assert notional(D("100.5"), D(2)) == D("201.0")
