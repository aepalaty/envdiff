"""Tests for key_timeline module."""

import pytest
from envdiff.key_timeline import (
    KeyTimelineCalculator,
    KeyTimeline,
    TimelineEntry,
    TimelineReport,
)
from envdiff.snapshot import Snapshot


@pytest.fixture
def calculator():
    return KeyTimelineCalculator()


def make_snapshot(env: dict, label: str) -> Snapshot:
    snap = Snapshot(env=env, label=label, captured_at=label)
    return snap


@pytest.fixture
def snapshots():
    s1 = make_snapshot({"DB_URL": "postgres://localhost", "DEBUG": "true"}, "v1")
    s2 = make_snapshot({"DB_URL": "postgres://prod", "DEBUG": "true"}, "v2")
    s3 = make_snapshot({"DB_URL": "postgres://prod", "DEBUG": "false", "NEW_KEY": "hello"}, "v3")
    return [s1, s2, s3]


def test_calculate_returns_report(calculator, snapshots):
    report = calculator.calculate(snapshots)
    assert isinstance(report, TimelineReport)


def test_all_keys_collected(calculator, snapshots):
    report = calculator.calculate(snapshots)
    assert "DB_URL" in report.timelines
    assert "DEBUG" in report.timelines
    assert "NEW_KEY" in report.timelines


def test_changed_key_detected(calculator, snapshots):
    report = calculator.calculate(snapshots)
    assert "DB_URL" in report.changed_keys
    assert "DEBUG" in report.changed_keys


def test_stable_key_not_in_changed(calculator):
    s1 = make_snapshot({"PORT": "8080"}, "v1")
    s2 = make_snapshot({"PORT": "8080"}, "v2")
    report = calculator.calculate([s1, s2])
    assert "PORT" in report.stable_keys
    assert "PORT" not in report.changed_keys


def test_missing_key_recorded_as_none(calculator, snapshots):
    report = calculator.calculate(snapshots)
    timeline = report.timelines["NEW_KEY"]
    assert timeline.entries[0].value is None
    assert timeline.entries[1].value is None
    assert timeline.entries[2].value == "hello"


def test_change_count_correct(calculator, snapshots):
    report = calculator.calculate(snapshots)
    db_timeline = report.timelines["DB_URL"]
    assert db_timeline.change_count == 1


def test_has_changes_true_when_values_differ(calculator, snapshots):
    report = calculator.calculate(snapshots)
    assert report.has_changes is True


def test_has_changes_false_when_all_stable(calculator):
    s1 = make_snapshot({"X": "1"}, "v1")
    s2 = make_snapshot({"X": "1"}, "v2")
    report = calculator.calculate([s1, s2])
    assert report.has_changes is False


def test_timeline_str_includes_key_and_labels(calculator, snapshots):
    report = calculator.calculate(snapshots)
    result = str(report.timelines["DB_URL"])
    assert "DB_URL" in result
    assert "v1" in result
    assert "v2" in result


def test_missing_value_shown_as_missing_in_str(calculator, snapshots):
    report = calculator.calculate(snapshots)
    result = str(report.timelines["NEW_KEY"])
    assert "<missing>" in result
