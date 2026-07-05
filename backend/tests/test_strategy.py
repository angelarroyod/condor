"""Multi-leg strategy analytics: payoff, breakevens, max profit/loss."""

from __future__ import annotations

from condor.options import Direction, LegKind
from condor.options.strategy import Leg, analyze

S, R, T = 100.0, 0.05, 0.5


def test_long_straddle_two_breakevens_unbounded_profit() -> None:
    legs = [
        Leg(LegKind.CALL, Direction.LONG, 100.0, 0.2),
        Leg(LegKind.PUT, Direction.LONG, 100.0, 0.2),
    ]
    a = analyze(legs, S, R, T)
    assert a.net_premium > 0  # long straddle is a debit
    assert len(a.breakevens) == 2
    assert a.breakevens[0] < 100.0 < a.breakevens[1]
    # Worst case is at the strike: lose the whole premium.
    assert abs(a.max_loss - (-a.net_premium)) < 1e-6
    assert a.max_profit_unbounded is True
    assert a.max_loss_unbounded is False


def test_bull_call_spread_bounded_both_sides() -> None:
    legs = [
        Leg(LegKind.CALL, Direction.LONG, 100.0, 0.2),
        Leg(LegKind.CALL, Direction.SHORT, 110.0, 0.2),
    ]
    a = analyze(legs, S, R, T)
    assert a.net_premium > 0  # debit spread
    assert a.max_profit_unbounded is False
    assert a.max_loss_unbounded is False
    assert abs(a.max_loss - (-a.net_premium)) < 1e-6
    assert abs(a.max_profit - (10.0 - a.net_premium)) < 1e-6
    assert len(a.breakevens) == 1
    assert abs(a.breakevens[0] - (100.0 + a.net_premium)) < 1e-2


def test_iron_condor_is_a_bounded_credit() -> None:
    legs = [
        Leg(LegKind.PUT, Direction.LONG, 85.0, 0.25),
        Leg(LegKind.PUT, Direction.SHORT, 90.0, 0.25),
        Leg(LegKind.CALL, Direction.SHORT, 110.0, 0.25),
        Leg(LegKind.CALL, Direction.LONG, 115.0, 0.25),
    ]
    a = analyze(legs, S, R, T)
    assert a.net_premium < 0  # net credit received
    assert a.max_profit_unbounded is False
    assert a.max_loss_unbounded is False
    # Best case keeps the whole credit.
    assert abs(a.max_profit - (-a.net_premium)) < 1e-6
    assert len(a.breakevens) == 2


def test_covered_call_caps_profit_with_stock_leg() -> None:
    # Long the underlying + short a call: bounded profit, no unbounded tail.
    legs = [
        Leg(LegKind.STOCK, Direction.LONG, 0.0, 0.0),
        Leg(LegKind.CALL, Direction.SHORT, 110.0, 0.2),
    ]
    a = analyze(legs, S, R, T)
    call_premium = a.legs[1].premium
    assert a.legs[0].premium == S  # stock "premium" is spot
    assert a.max_profit_unbounded is False
    assert a.max_loss_unbounded is False
    # Above the strike the payoff flattens at (strike - spot) + call credit.
    assert abs(a.max_profit - (10.0 + call_premium)) < 1e-6
    # Stock contributes delta 1; short call subtracts its delta.
    assert abs(a.aggregate.delta - (1.0 - a.legs[1].greeks.delta)) < 1e-9


def test_aggregate_delta_sums_legs() -> None:
    legs = [
        Leg(LegKind.CALL, Direction.LONG, 100.0, 0.2, quantity=2.0),
        Leg(LegKind.PUT, Direction.SHORT, 100.0, 0.2),
    ]
    a = analyze(legs, S, R, T)
    expected = 2.0 * a.legs[0].greeks.delta - 1.0 * a.legs[1].greeks.delta
    assert abs(a.aggregate.delta - expected) < 1e-12

