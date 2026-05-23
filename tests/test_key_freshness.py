import pytest
from envdiff.key_freshness import FreshnessCalculator, FreshnessReport
from envdiff.freshness_formatter import FreshnessFormatter


@pytest.fixture
def calculator():
    return FreshnessCalculator()


@pytest.fixture
def three_snapshots():
    return [
        {"prod": {"DB_URL": "postgres://old", "APP_NAME": "myapp"},
         "staging": {"DB_URL": "postgres://stg", "APP_NAME": "myapp"}},
        {"prod": {"DB_URL": "postgres://new", "APP_NAME": "myapp", "SECRET": "abc"},
         "staging": {"DB_URL": "postgres://stg", "APP_NAME": "myapp"}},
        {"prod": {"DB_URL": "postgres://new", "APP_NAME": "myapp"},
         "staging": {"DB_URL": "postgres://stg", "APP_NAME": "myapp"}},
    ]


def test_calculate_returns_report(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    assert isinstance(report, FreshnessReport)


def test_env_names_captured(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    assert "prod" in report.env_names
    assert "staging" in report.env_names


def test_all_keys_collected(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    keys = {e.key for e in report.entries}
    assert "DB_URL" in keys
    assert "APP_NAME" in keys
    assert "SECRET" in keys


def test_stale_key_detected(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    stale = {e.key for e in report.stale_keys}
    assert "SECRET" in stale


def test_fresh_key_not_stale(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    fresh = {e.key for e in report.fresh_keys}
    assert "DB_URL" in fresh
    assert "APP_NAME" in fresh


def test_snapshot_count_correct(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    secret_entry = next(e for e in report.entries if e.key == "SECRET")
    assert secret_entry.snapshot_count == 1

    db_entry = next(e for e in report.entries if e.key == "DB_URL")
    assert db_entry.snapshot_count == 3


def test_empty_snapshots_returns_empty(calculator):
    report = calculator.calculate([])
    assert report.entries == []
    assert not report.has_stale


def test_has_stale_flag(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    assert report.has_stale is True


def test_formatter_includes_header():
    fmt = FreshnessFormatter(color=False)
    report = FreshnessReport(env_names=["prod"], entries=[])
    output = fmt.format_report(report)
    assert "Freshness" in output


def test_formatter_marks_stale(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    fmt = FreshnessFormatter(color=False)
    output = fmt.format_report(report)
    assert "STALE" in output
    assert "SECRET" in output


def test_formatter_summary_line(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    fmt = FreshnessFormatter(color=False)
    output = fmt.format_report(report)
    assert "Summary" in output
    assert "stale" in output.lower()
