"""Unit tests for the reconnect backoff schedule."""

from __future__ import annotations

from condor.ingest.reconnect import Backoff


def test_ceiling_grows_exponentially_and_caps() -> None:
    # rand()==1.0 makes next_delay return the full ceiling for each attempt.
    b = Backoff(base=1.0, factor=2.0, cap=10.0, rand=lambda: 1.0)
    assert [b.next_delay() for _ in range(5)] == [1.0, 2.0, 4.0, 8.0, 10.0]


def test_jitter_stays_within_ceiling() -> None:
    b = Backoff(base=1.0, factor=2.0, cap=60.0, rand=lambda: 0.5)
    assert b.next_delay() == 0.5  # 0.5 * 1
    assert b.next_delay() == 1.0  # 0.5 * 2


def test_reset_returns_to_base() -> None:
    b = Backoff(base=1.0, factor=2.0, cap=60.0, rand=lambda: 1.0)
    b.next_delay()
    b.next_delay()
    b.reset()
    assert b.next_delay() == 1.0
