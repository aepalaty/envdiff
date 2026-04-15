"""Tests for envdiff.key_padding."""

import pytest
from envdiff.key_padding import PaddingDetector, PaddingIssue, PaddingReport


@pytest.fixture
def detector():
    return PaddingDetector()


@pytest.fixture
def three_envs():
    return {
        "dev": {
            "DB_URL": "postgres://localhost",
            "APP_NAME": " myapp",       # leading space
            "SECRET_KEY": "abc123",
        },
        "staging": {
            "DB_URL": "postgres://staging",
            "APP_NAME": "myapp ",       # trailing space
            "SECRET_KEY": "abc123",
        },
        "prod": {
            "DB_URL": "postgres://prod",
            "APP_NAME": "myapp",         # clean
            "SECRET_KEY": " secret ",   # both
        },
    }


def test_calculate_returns_report(detector, three_envs):
    report = detector.detect(three_envs)
    assert isinstance(report, PaddingReport)


def test_env_names_captured(detector, three_envs):
    report = detector.detect(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_clean_env_has_no_issues(detector):
    envs = {"prod": {"KEY": "value", "OTHER": "clean"}}
    report = detector.detect(envs)
    assert not report.has_issues
    assert report.issues == []


def test_detects_leading_whitespace(detector, three_envs):
    report = detector.detect(three_envs)
    dev_issues = report.issues_for_env("dev")
    assert any(i.key == "APP_NAME" and i.leading for i in dev_issues)


def test_detects_trailing_whitespace(detector, three_envs):
    report = detector.detect(three_envs)
    staging_issues = report.issues_for_env("staging")
    assert any(i.key == "APP_NAME" and i.trailing for i in staging_issues)


def test_detects_both_leading_and_trailing(detector, three_envs):
    report = detector.detect(three_envs)
    prod_issues = report.issues_for_env("prod")
    secret_issue = next((i for i in prod_issues if i.key == "SECRET_KEY"), None)
    assert secret_issue is not None
    assert secret_issue.leading
    assert secret_issue.trailing


def test_affected_keys_returns_unique_keys(detector, three_envs):
    report = detector.detect(three_envs)
    affected = report.affected_keys
    assert "APP_NAME" in affected
    assert "SECRET_KEY" in affected
    assert len(affected) == len(set(affected))


def test_has_issues_true_when_padding_found(detector, three_envs):
    report = detector.detect(three_envs)
    assert report.has_issues


def test_str_includes_direction(detector):
    issue = PaddingIssue(
        key="MY_KEY",
        env_name="dev",
        raw_value=" value",
        leading=True,
        trailing=False,
    )
    assert "leading" in str(issue)
    assert "MY_KEY" in str(issue)
    assert "dev" in str(issue)


def test_issues_for_env_filters_correctly(detector, three_envs):
    report = detector.detect(three_envs)
    dev_issues = report.issues_for_env("dev")
    assert all(i.env_name == "dev" for i in dev_issues)
