import pytest
from envdiff.key_lineage import LineageCalculator, LineageReport, LineageEntry


@pytest.fixture
def calculator():
    return LineageCalculator()


@pytest.fixture
def three_snapshots():
    return [
        {"label": "v1", "env": {"DB_URL": "postgres://localhost", "APP_NAME": "myapp"}},
        {"label": "v2", "env": {"DB_URL": "postgres://prod", "APP_NAME": "myapp", "SECRET": "abc"}},
        {"label": "v3", "env": {"DB_URL": "postgres://prod", "APP_NAME": "myapp", "SECRET": "xyz"}},
    ]


def test_calculate_returns_report(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    assert isinstance(report, LineageReport)


def test_all_keys_collected(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    assert "DB_URL" in report.all_keys
    assert "APP_NAME" in report.all_keys
    assert "SECRET" in report.all_keys


def test_db_url_changed_once(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    entry = report.get("DB_URL")
    assert entry is not None
    assert entry.change_count == 1


def test_app_name_never_changed(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    entry = report.get("APP_NAME")
    assert entry is not None
    assert entry.change_count == 0


def test_secret_introduced_in_v2(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    entry = report.get("SECRET")
    assert entry is not None
    assert entry.introduced_in == "v2"


def test_secret_changed_in_v3(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    entry = report.get("SECRET")
    assert entry.change_count == 1
    change_event = next(e for e in entry.events if e.changed_from is not None)
    assert change_event.changed_from == "abc"
    assert change_event.value == "xyz"
    assert change_event.snapshot_label == "v3"


def test_current_value_reflects_latest(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    assert report.get("DB_URL").current_value == "postgres://prod"


def test_empty_snapshots_returns_empty_report(calculator):
    report = calculator.calculate([])
    assert report.all_keys == []


def test_single_snapshot_no_changes(calculator):
    snaps = [{"label": "v1", "env": {"KEY": "val"}}]
    report = calculator.calculate(snaps)
    entry = report.get("KEY")
    assert entry is not None
    assert entry.change_count == 0
    assert entry.introduced_in == "v1"


def test_str_representation(calculator, three_snapshots):
    report = calculator.calculate(three_snapshots)
    entry = report.get("SECRET")
    s = str(entry)
    assert "SECRET" in s
    assert "event" in s
