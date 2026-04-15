"""Tests for envdiff.key_encoding."""
import pytest
from envdiff.key_encoding import EncodingChecker, EncodingIssue, EncodingReport


@pytest.fixture
def checker():
    return EncodingChecker()


@pytest.fixture
def clean_envs():
    return {
        "production": {"DB_URL": "postgres://localhost/mydb", "PORT": "5432"},
        "staging": {"DB_URL": "postgres://staging/mydb", "PORT": "5433"},
    }


def test_clean_env_returns_no_issues(checker, clean_envs):
    report = checker.check(clean_envs)
    assert isinstance(report, EncodingReport)
    assert not report.has_issues


def test_env_names_captured(checker, clean_envs):
    report = checker.check(clean_envs)
    assert "production" in report.env_names
    assert "staging" in report.env_names


def test_detects_non_ascii_value(checker):
    envs = {"prod": {"APP_NAME": "caf\u00e9"}}
    report = checker.check(envs)
    assert report.has_issues
    issue = report.issues[0]
    assert issue.issue_type == "non_ascii"
    assert issue.key == "APP_NAME"
    assert issue.env_name == "prod"


def test_detects_null_byte(checker):
    envs = {"prod": {"SECRET": "abc\x00def"}}
    report = checker.check(envs)
    assert report.has_issues
    types = [i.issue_type for i in report.issues]
    assert "null_byte" in types


def test_detects_control_character(checker):
    envs = {"prod": {"TOKEN": "abc\x01def"}}
    report = checker.check(envs)
    assert report.has_issues
    types = [i.issue_type for i in report.issues]
    assert "control_char" in types


def test_detects_mixed_line_endings(checker):
    envs = {"prod": {"MULTILINE": "line1\r\nline2"}}
    report = checker.check(envs)
    assert report.has_issues
    types = [i.issue_type for i in report.issues]
    assert "mixed_line_ending" in types


def test_issues_for_env_filters_correctly(checker):
    envs = {
        "prod": {"KEY": "caf\u00e9"},
        "staging": {"KEY": "clean"},
    }
    report = checker.check(envs)
    prod_issues = report.issues_for_env("prod")
    staging_issues = report.issues_for_env("staging")
    assert len(prod_issues) >= 1
    assert len(staging_issues) == 0


def test_issues_for_key_filters_correctly(checker):
    envs = {"prod": {"BAD_KEY": "\x00", "GOOD_KEY": "hello"}}
    report = checker.check(envs)
    bad = report.issues_for_key("BAD_KEY")
    good = report.issues_for_key("GOOD_KEY")
    assert len(bad) >= 1
    assert len(good) == 0


def test_issue_str_representation(checker):
    envs = {"prod": {"X": "caf\u00e9"}}
    report = checker.check(envs)
    assert len(report.issues) > 0
    s = str(report.issues[0])
    assert "prod" in s
    assert "X" in s
    assert "non_ascii" in s


def test_multiple_issues_same_key(checker):
    # null byte AND non-ascii in same value
    envs = {"prod": {"WEIRD": "caf\u00e9\x00end"}}
    report = checker.check(envs)
    types = {i.issue_type for i in report.issues}
    assert "null_byte" in types
    assert "non_ascii" in types
