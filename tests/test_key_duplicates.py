"""Tests for envdiff.key_duplicates."""

import pytest
from envdiff.key_duplicates import DuplicateDetector, DuplicateEntry, DuplicateReport


@pytest.fixture
def detector():
    return DuplicateDetector()


CLEAN_LINES = [
    "DB_HOST=localhost\n",
    "DB_PORT=5432\n",
    "APP_ENV=production\n",
]

DUPLICATE_LINES = [
    "DB_HOST=localhost\n",
    "DB_PORT=5432\n",
    "DB_HOST=remotehost\n",
    "APP_ENV=production\n",
    "APP_ENV=staging\n",
]

COMMENT_LINES = [
    "# DB_HOST=ignored\n",
    "DB_HOST=localhost\n",
    "\n",
    "DB_HOST=other\n",
]

EXPORT_LINES = [
    "export TOKEN=abc\n",
    "export TOKEN=xyz\n",
]


def test_clean_env_has_no_duplicates(detector):
    report = detector.detect("prod.env", CLEAN_LINES)
    assert not report.has_duplicates
    assert report.duplicate_keys == []


def test_duplicate_env_detected(detector):
    report = detector.detect("dev.env", DUPLICATE_LINES)
    assert report.has_duplicates
    assert "DB_HOST" in report.duplicate_keys
    assert "APP_ENV" in report.duplicate_keys


def test_duplicate_entry_has_correct_line_numbers(detector):
    report = detector.detect("dev.env", DUPLICATE_LINES)
    db_host = next(d for d in report.duplicates if d.key == "DB_HOST")
    assert db_host.line_numbers == [1, 3]


def test_duplicate_entry_captures_all_values(detector):
    report = detector.detect("dev.env", DUPLICATE_LINES)
    db_host = next(d for d in report.duplicates if d.key == "DB_HOST")
    assert "localhost" in db_host.values
    assert "remotehost" in db_host.values


def test_comments_are_not_treated_as_keys(detector):
    report = detector.detect("test.env", COMMENT_LINES)
    assert report.has_duplicates
    db_host = next(d for d in report.duplicates if d.key == "DB_HOST")
    # line 1 is a comment, so first real occurrence is line 2
    assert 1 not in db_host.line_numbers
    assert 2 in db_host.line_numbers


def test_export_prefix_handled(detector):
    report = detector.detect("export.env", EXPORT_LINES)
    assert report.has_duplicates
    assert "TOKEN" in report.duplicate_keys


def test_str_clean_report(detector):
    report = detector.detect("clean.env", CLEAN_LINES)
    assert "no duplicate" in str(report)


def test_str_dirty_report(detector):
    report = detector.detect("dirty.env", DUPLICATE_LINES)
    output = str(report)
    assert "DB_HOST" in output
    assert "APP_ENV" in output


def test_duplicate_entry_str(detector):
    entry = DuplicateEntry(key="FOO", values=["a", "b"], line_numbers=[2, 7])
    result = str(entry)
    assert "FOO" in result
    assert "2" in result
    assert "7" in result
