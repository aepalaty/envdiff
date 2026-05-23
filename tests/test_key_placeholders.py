"""Tests for envdiff.key_placeholders."""
import pytest
from envdiff.key_placeholders import PlaceholderChecker, PlaceholderReport


@pytest.fixture
def checker():
    return PlaceholderChecker()


@pytest.fixture
def three_envs():
    return {
        "production": {
            "DB_URL": "postgres://prod-host/db",
            "SECRET_KEY": "s3cr3t-real-value",
            "API_KEY": "live_key_abc123",
        },
        "staging": {
            "DB_URL": "postgres://staging-host/db",
            "SECRET_KEY": "changeme",
            "API_KEY": "placeholder",
        },
        "development": {
            "DB_URL": "postgres://localhost/db",
            "SECRET_KEY": "your_value_here",
            "API_KEY": "xxxx",
        },
    }


def test_calculate_returns_report(checker, three_envs):
    report = checker.calculate(three_envs)
    assert isinstance(report, PlaceholderReport)


def test_env_names_captured(checker, three_envs):
    report = checker.calculate(three_envs)
    assert set(report.env_names) == {"production", "staging", "development"}


def test_clean_env_has_no_issues(checker):
    envs = {"prod": {"DB_URL": "postgres://real-host/db", "PORT": "5432"}}
    report = checker.calculate(envs)
    assert not report.has_issues
    assert report.issues == []


def test_detects_changeme(checker):
    envs = {"dev": {"SECRET_KEY": "changeme"}}
    report = checker.calculate(envs)
    assert report.has_issues
    assert any(i.key == "SECRET_KEY" for i in report.issues)


def test_detects_placeholder_word(checker):
    envs = {"dev": {"API_TOKEN": "placeholder"}}
    report = checker.calculate(envs)
    assert report.has_issues


def test_detects_xxxx(checker):
    envs = {"dev": {"API_KEY": "xxxx"}}
    report = checker.calculate(envs)
    assert report.has_issues


def test_detects_angle_bracket_pattern(checker):
    envs = {"dev": {"DB_PASS": "<your-password-here>"}}
    report = checker.calculate(envs)
    assert report.has_issues


def test_empty_value_is_not_a_placeholder(checker):
    envs = {"dev": {"OPTIONAL_KEY": ""}}
    report = checker.calculate(envs)
    assert not report.has_issues


def test_issues_for_env_filters_correctly(checker, three_envs):
    report = checker.calculate(three_envs)
    staging_issues = report.issues_for_env("staging")
    assert all(i.env_name == "staging" for i in staging_issues)
    assert len(staging_issues) >= 1


def test_affected_keys_returns_unique_sorted(checker, three_envs):
    report = checker.calculate(three_envs)
    keys = report.affected_keys
    assert keys == sorted(set(keys))
    assert "SECRET_KEY" in keys
    assert "API_KEY" in keys


def test_issue_str_representation(checker):
    envs = {"dev": {"TOKEN": "changeme"}}
    report = checker.calculate(envs)
    assert len(report.issues) == 1
    assert "dev" in str(report.issues[0])
    assert "TOKEN" in str(report.issues[0])
    assert "placeholder" in str(report.issues[0]).lower() or "changeme" in str(report.issues[0])


def test_detection_is_case_insensitive(checker):
    envs = {"dev": {"SECRET": "CHANGEME"}}
    report = checker.calculate(envs)
    assert report.has_issues


def test_production_env_is_clean(checker, three_envs):
    report = checker.calculate(three_envs)
    prod_issues = report.issues_for_env("production")
    assert prod_issues == []
