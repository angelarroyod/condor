"""Average-cost engine tests — open/add/reduce/close/flip, long and short."""

from __future__ import annotations

from decimal import Decimal

import pytest

from condor.engine.position import PositionState, apply_fill

D = Decimal


def test_open_long_from_flat() -> None:
    state, realized = apply_fill(PositionState(), "buy", D(10), D(100))
    assert (state.quantity, state.avg_price, state.realized_pnl) == (D(10), D(100), D(0))
    assert realized == D(0)


def test_add_to_long_reaverages() -> None:
    state = PositionState(D(10), D(100))
    state, realized = apply_fill(state, "buy", D(10), D(120))
    assert state.quantity == D(20)
    assert state.avg_price == D(110)
    assert realized == D(0)


def test_partial_close_long_realizes() -> None:
    state = PositionState(D(20), D(110))
    state, realized = apply_fill(state, "sell", D(5), D(130))
    assert realized == D(100)  # 5 * (130 - 110)
    assert state.quantity == D(15)
    assert state.avg_price == D(110)  # avg unchanged on reduce


def test_full_close_returns_to_flat() -> None:
    state = PositionState(D(15), D(110), realized_pnl=D(100))
    state, realized = apply_fill(state, "sell", D(15), D(90))
    assert realized == D(-300)  # 15 * (90 - 110)
    assert state.quantity == D(0)
    assert state.avg_price == D(0)
    assert state.realized_pnl == D(-200)  # cumulative


def test_flip_long_to_short() -> None:
    state = PositionState(D(10), D(100))
    state, realized = apply_fill(state, "sell", D(15), D(120))
    assert realized == D(200)  # close 10 * (120 - 100)
    assert state.quantity == D(-5)  # 5 short remainder
    assert state.avg_price == D(120)  # fresh lot at fill price


def test_open_and_cover_short() -> None:
    state, _ = apply_fill(PositionState(), "sell", D(10), D(100))
    assert state.quantity == D(-10)
    assert state.avg_price == D(100)
    state, realized = apply_fill(state, "buy", D(4), D(90))
    assert realized == D(40)  # short profits: 4 * (100 - 90)
    assert state.quantity == D(-6)
    assert state.avg_price == D(100)


def test_add_to_short_reaverages() -> None:
    state = PositionState(D(-10), D(100))
    state, realized = apply_fill(state, "sell", D(10), D(120))
    assert state.quantity == D(-20)
    assert state.avg_price == D(110)
    assert realized == D(0)


def test_flip_short_to_long() -> None:
    state = PositionState(D(-10), D(100))
    state, realized = apply_fill(state, "buy", D(15), D(80))
    assert realized == D(200)  # cover 10 * (100 - 80)
    assert state.quantity == D(5)
    assert state.avg_price == D(80)


def test_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="positive"):
        apply_fill(PositionState(), "buy", D(0), D(100))
    with pytest.raises(ValueError, match="invalid side"):
        apply_fill(PositionState(), "hold", D(1), D(100))
