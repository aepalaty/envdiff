"""Tests for KeyUsageTracker and KeyUsageReport."""

import pytest
from envdiff.key_usage import KeyUsageTracker, KeyUsageReport, KeyUsageRecord


@pytest.fixture
def tracker():
    return KeyUsageTracker()


@pytest.fixture
def three_envs():
    return {
        "prod": {"DB_URL": "postgres://prod", "SECRET_KEY": "abc", "PORT": "5432"},
        "staging": {"DB_URL": "postgres://staging", "SECRET_KEY": "xyz", "DEBUG": "true"},
        "dev": {"DB_URL": "postgres://dev", "DEBUG": "true", "LOCAL_ONLY": "1"},
    }


def test_track_returns_report(tracker, three_envs):
    report = tracker.track(three_envs)
    assert isinstance(report, KeyUsageReport)


def test_total_keys_counts_unique(tracker, three_envs):
    report = tracker.track(three_envs)
    expected_keys = {"DB_URL", "SECRET_KEY", "PORT", "DEBUG", "LOCAL_ONLY"}
    assert report.total_keys == len(expected_keys)


def test_db_url_seen_in_all_envs(tracker, three_envs):
    report = tracker.track(three_envs)
    record = report.records["DB_URL"]
    assert set(record.seen_in) == {"prod", "staging", "dev"}
    assert record.occurrence_count == 3


def test_local_only_seen_in_one_env(tracker, three_envs):
    report = tracker.track(three_envs)
    record = report.records["LOCAL_ONLY"]
    assert record.seen_in == ["dev"]
    assert record.occurrence_count == 1


def test_most_common_returns_sorted(tracker, three_envs):
    report = tracker.track(three_envs)
    most = report.most_common(3)
    assert most[0].key == "DB_URL"
    assert most[0].occurrence_count >= most[1].occurrence_count


def test_least_common_returns_sorted(tracker, three_envs):
    report = tracker.track(three_envs)
    least = report.least_common(2)
    assert least[0].occurrence_count <= least[1].occurrence_count


def test_record_last_seen_is_set(tracker, three_envs):
    report = tracker.track(three_envs)
    for record in report.records.values():
        assert record.last_seen is not None


def test_record_roundtrip(tracker, three_envs):
    report = tracker.track(three_envs)
    record = report.records["DB_URL"]
    restored = KeyUsageRecord.from_dict(record.to_dict())
    assert restored.key == record.key
    assert restored.occurrence_count == record.occurrence_count
    assert restored.seen_in == record.seen_in


def test_empty_envs_returns_empty_report(tracker):
    report = tracker.track({})
    assert report.total_keys == 0
    assert report.most_common() == []
