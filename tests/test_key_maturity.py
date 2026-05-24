import pytest
from envdiff.key_maturity import MaturityCalculator, MaturityReport, _classify
from envdiff.maturity_formatter import MaturityFormatter
from envdiff.snapshot import Snapshot
from datetime import datetime


def make_snapshot(label: str, env: dict) -> Snapshot:
    return Snapshot(path=label, label=label, env=env, captured_at=datetime.utcnow().isoformat())


@pytest.fixture
def calculator():
    return MaturityCalculator()


@pytest.fixture
def three_snapshots():
    s1 = make_snapshot("v1", {"DB_URL": "a", "APP_NAME": "app", "NEW_KEY": "x"})
    s2 = make_snapshot("v2", {"DB_URL": "b", "APP_NAME": "app"})
    s3 = make_snapshot("v3", {"DB_URL": "c", "APP_NAME": "app"})
    return [s1, s2, s3]


def test_calculate_returns_report(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    assert isinstance(report, MaturityReport)


def test_all_keys_collected(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    keys = {e.key for e in report.entries}
    assert "DB_URL" in keys
    assert "APP_NAME" in keys
    assert "NEW_KEY" in keys


def test_env_names_captured(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    assert "v1" in report.env_names
    assert "v3" in report.env_names


def test_stable_key_appears_in_all_snapshots(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    db_entry = next(e for e in report.entries if e.key == "DB_URL")
    assert db_entry.appearances == 3
    assert db_entry.label == "stable"


def test_transient_key_appears_once(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    new_entry = next(e for e in report.entries if e.key == "NEW_KEY")
    assert new_entry.appearances == 1
    assert new_entry.label in ("emerging", "transient")


def test_empty_snapshots_returns_empty_report(calculator):
    report = calculator.calculate([])
    assert report.entries == []


def test_classify_stable():
    assert _classify(10, 10) == "stable"


def test_classify_transient():
    assert _classify(0, 10) == "transient"


def test_maturity_ratio(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    app_entry = next(e for e in report.entries if e.key == "APP_NAME")
    assert app_entry.maturity_ratio == pytest.approx(1.0)


def test_stable_keys_property(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    stable = report.stable_keys
    assert all(e.label == "stable" for e in stable)


def test_format_report_includes_header(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    formatter = MaturityFormatter(color=False)
    output = formatter.format_report(report)
    assert "Maturity" in output
    assert "DB_URL" in output


def test_format_report_empty():
    formatter = MaturityFormatter(color=False)
    output = formatter.format_report(MaturityReport())
    assert "No maturity" in output
