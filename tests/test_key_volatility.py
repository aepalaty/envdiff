"""Tests for key_volatility and volatility_formatter."""
from __future__ import annotations
import pytest
from envdiff.key_volatility import VolatilityCalculator, VolatilityReport
from envdiff.volatility_formatter import VolatilityFormatter


@pytest.fixture
def calculator():
    return VolatilityCalculator()


@pytest.fixture
def three_snapshots():
    return [
        {"DB_URL": "postgres://localhost/dev", "PORT": "8000", "SECRET": "abc"},
        {"DB_URL": "postgres://localhost/staging", "PORT": "8000", "SECRET": "xyz"},
        {"DB_URL": "postgres://localhost/prod", "PORT": "8000", "SECRET": "xyz"},
    ]


def test_calculate_returns_report(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    assert isinstance(report, VolatilityReport)


def test_all_keys_collected(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    keys = {e.key for e in report.entries}
    assert keys == {"DB_URL", "PORT", "SECRET"}


def test_stable_key_has_zero_changes(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    port_entry = next(e for e in report.entries if e.key == "PORT")
    assert port_entry.change_count == 0
    assert port_entry.volatility_ratio == 0.0
    assert not port_entry.is_volatile


def test_volatile_key_detected(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    db_entry = next(e for e in report.entries if e.key == "DB_URL")
    assert db_entry.change_count == 2
    assert db_entry.volatility_ratio == 1.0
    assert db_entry.is_volatile


def test_partial_change_ratio(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    secret_entry = next(e for e in report.entries if e.key == "SECRET")
    assert secret_entry.change_count == 1
    assert secret_entry.volatility_ratio == pytest.approx(0.5)


def test_empty_snapshots_returns_empty_report(calculator):
    report = calculator.calculate([])
    assert report.entries == []
    assert not report.has_volatile_keys


def test_single_snapshot_zero_volatility(calculator):
    report = calculator.calculate([{"KEY": "value"}])
    assert report.entries[0].volatility_ratio == 0.0


def test_volatile_keys_property(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    volatile = report.volatile_keys
    assert all(e.is_volatile for e in volatile)


def test_stable_keys_property(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    stable = report.stable_keys
    assert all(not e.is_volatile for e in stable)


def test_average_volatility(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    assert 0.0 < report.average_volatility <= 1.0


def test_values_seen_deduplicated(calculator):
    snaps = [
        {"KEY": "a"},
        {"KEY": "b"},
        {"KEY": "a"},
    ]
    report = calculator.calculate(snaps)
    entry = report.entries[0]
    assert "a" in entry.values_seen
    assert "b" in entry.values_seen


def test_formatter_produces_output(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    formatter = VolatilityFormatter(color=False)
    output = formatter.format_report(report)
    assert "Volatility" in output
    assert "DB_URL" in output
    assert "PORT" in output


def test_formatter_marks_volatile(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    formatter = VolatilityFormatter(color=False)
    output = formatter.format_report(report)
    assert "VOLATILE" in output


def test_formatter_empty_report():
    formatter = VolatilityFormatter(color=False)
    output = formatter.format_report(VolatilityReport())
    assert "No volatility" in output
