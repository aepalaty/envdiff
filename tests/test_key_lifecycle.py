import pytest
from envdiff.key_lifecycle import LifecycleCalculator, LifecycleReport
from envdiff.lifecycle_formatter import LifecycleFormatter


@pytest.fixture
def calculator():
    return LifecycleCalculator()


@pytest.fixture
def snapshots():
    return [
        {"label": "v1", "env": {"DB_URL": "postgres://localhost", "PORT": "5432"}},
        {"label": "v2", "env": {"DB_URL": "postgres://prod", "PORT": "5432", "NEW_KEY": "hello"}},
        {"label": "v3", "env": {"DB_URL": "postgres://prod", "NEW_KEY": "hello"}},
    ]


def test_calculate_returns_report(calculator, snapshots):
    report = calculator.calculate(snapshots)
    assert isinstance(report, LifecycleReport)


def test_all_keys_collected(calculator, snapshots):
    report = calculator.calculate(snapshots)
    assert set(report.all_keys) == {"DB_URL", "PORT", "NEW_KEY"}


def test_db_url_modified_in_v2(calculator, snapshots):
    report = calculator.calculate(snapshots)
    entry = report.entry_for("DB_URL")
    statuses = [e.status for e in entry.events]
    assert statuses[0] == "added"
    assert statuses[1] == "modified"
    assert statuses[2] == "unchanged"


def test_port_removed_in_v3(calculator, snapshots):
    report = calculator.calculate(snapshots)
    entry = report.entry_for("PORT")
    statuses = [e.status for e in entry.events]
    assert "removed" in statuses
    assert entry.last_removed == "v3"


def test_new_key_added_in_v2(calculator, snapshots):
    report = calculator.calculate(snapshots)
    entry = report.entry_for("NEW_KEY")
    assert entry.first_seen == "v2"
    assert entry.events[0].status == "added"


def test_change_count_for_stable_key(calculator, snapshots):
    report = calculator.calculate(snapshots)
    entry = report.entry_for("NEW_KEY")
    # added in v2, unchanged in v3 — 1 change
    assert entry.change_count == 1


def test_empty_snapshots_returns_empty_report(calculator):
    report = calculator.calculate([])
    assert report.entries == []


def test_single_snapshot_all_added(calculator):
    snaps = [{"label": "only", "env": {"A": "1", "B": "2"}}]
    report = calculator.calculate(snaps)
    for entry in report.entries:
        assert entry.events[0].status == "added"


def test_formatter_format_report(calculator, snapshots):
    report = calculator.calculate(snapshots)
    formatter = LifecycleFormatter(color=False)
    output = formatter.format_report(report)
    assert "DB_URL" in output
    assert "modified" in output
    assert "removed" in output


def test_formatter_format_summary(calculator, snapshots):
    report = calculator.calculate(snapshots)
    formatter = LifecycleFormatter(color=False)
    summary = formatter.format_summary(report)
    assert "Total keys tracked" in summary
    assert "3" in summary


def test_formatter_empty_report():
    formatter = LifecycleFormatter(color=False)
    output = formatter.format_report(LifecycleReport())
    assert "No lifecycle data" in output
