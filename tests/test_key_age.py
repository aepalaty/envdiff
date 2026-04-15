"""Tests for key age calculation."""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

from envdiff.key_age import KeyAgeCalculator, AgeReport, AgeEntry


def make_snapshot(env: dict, days_ago: int) -> MagicMock:
    snap = MagicMock()
    snap.env = env
    snap.timestamp = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return snap


@pytest.fixture
def calculator():
    return KeyAgeCalculator()


def test_empty_snapshots_returns_empty_report(calculator):
    report = calculator.calculate([])
    assert isinstance(report, AgeReport)
    assert report.entries == []


def test_single_snapshot_creates_entries(calculator):
    snap = make_snapshot({"DB_URL": "postgres://", "SECRET": "abc"}, days_ago=10)
    report = calculator.calculate([snap])
    keys = [e.key for e in report.entries]
    assert "DB_URL" in keys
    assert "SECRET" in keys


def test_unchanged_key_has_zero_changes(calculator):
    snap1 = make_snapshot({"DB_URL": "postgres://"}, days_ago=30)
    snap2 = make_snapshot({"DB_URL": "postgres://"}, days_ago=10)
    report = calculator.calculate([snap1, snap2])
    entry = next(e for e in report.entries if e.key == "DB_URL")
    assert entry.change_count == 0


def test_changed_key_increments_change_count(calculator):
    snap1 = make_snapshot({"SECRET": "old"}, days_ago=60)
    snap2 = make_snapshot({"SECRET": "new"}, days_ago=5)
    report = calculator.calculate([snap1, snap2])
    entry = next(e for e in report.entries if e.key == "SECRET")
    assert entry.change_count == 1


def test_stale_key_flagged_after_90_days(calculator):
    snap = make_snapshot({"OLD_KEY": "value"}, days_ago=100)
    report = calculator.calculate([snap])
    entry = next(e for e in report.entries if e.key == "OLD_KEY")
    assert entry.is_stale is True


def test_recent_key_not_stale(calculator):
    snap = make_snapshot({"FRESH_KEY": "value"}, days_ago=5)
    report = calculator.calculate([snap])
    entry = next(e for e in report.entries if e.key == "FRESH_KEY")
    assert entry.is_stale is False


def test_has_stale_returns_true_when_stale_keys_exist(calculator):
    snap = make_snapshot({"ANCIENT": "v"}, days_ago=200)
    report = calculator.calculate([snap])
    assert report.has_stale is True


def test_stale_keys_property_filters_correctly(calculator):
    snap1 = make_snapshot({"OLD": "v"}, days_ago=120)
    snap2 = make_snapshot({"NEW": "v"}, days_ago=2)
    report = calculator.calculate([snap1, snap2])
    stale_keys = [e.key for e in report.stale_keys]
    assert "OLD" in stale_keys
    assert "NEW" not in stale_keys


def test_entries_sorted_by_days_desc(calculator):
    snap = make_snapshot({"A": "1", "B": "2", "C": "3"}, days_ago=50)
    snap2 = make_snapshot({"A": "1", "B": "changed", "C": "3"}, days_ago=10)
    report = calculator.calculate([snap, snap2])
    days = [e.days_since_change for e in report.entries]
    assert days == sorted(days, reverse=True)


def test_average_days_since_change(calculator):
    snap1 = make_snapshot({"K1": "v"}, days_ago=100)
    snap2 = make_snapshot({"K2": "v"}, days_ago=0)
    report = calculator.calculate([snap1, snap2])
    avg = report.average_days_since_change
    assert 40 <= avg <= 60  # roughly 50 days average
