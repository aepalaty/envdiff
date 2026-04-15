"""Tests for envdiff.key_secrets."""

import pytest

from envdiff.key_secrets import (
    SecretsChecker,
    SecretsReport,
    SecretIssue,
    _is_sensitive_key,
    _is_placeholder,
)


@pytest.fixture
def checker():
    return SecretsChecker()


@pytest.fixture
def clean_envs():
    return {
        "production": {
            "DB_HOST": "db.example.com",
            "API_KEY": "xK9#mP2$qL7!nR4@vT6&wY1",
            "SECRET_KEY": "aB3!cD5@eF7#gH9$iJ1%kL2^",
        },
        "staging": {
            "DB_HOST": "staging-db.example.com",
            "API_KEY": "zM8*oN3(pQ6)rS0_uV4+xW5-",
            "SECRET_KEY": "bC4@dE6#fG8$hI0%jK2^lM3&",
        },
    }


def test_is_sensitive_key_detects_patterns():
    assert _is_sensitive_key("API_KEY") is True
    assert _is_sensitive_key("DB_PASSWORD") is True
    assert _is_sensitive_key("AUTH_TOKEN") is True
    assert _is_sensitive_key("SIGNING_SECRET") is True
    assert _is_sensitive_key("PRIVATE_KEY") is True


def test_is_sensitive_key_ignores_non_sensitive():
    assert _is_sensitive_key("DB_HOST") is False
    assert _is_sensitive_key("PORT") is False
    assert _is_sensitive_key("APP_ENV") is False


def test_is_placeholder_detects_common_placeholders():
    assert _is_placeholder("changeme") is True
    assert _is_placeholder("your_secret_here") is True
    assert _is_placeholder("<replace_me>") is True
    assert _is_placeholder("xxxx1234") is True


def test_is_placeholder_ignores_real_values():
    assert _is_placeholder("xK9#mP2$qL7") is False
    assert _is_placeholder("supersecret123") is False


def test_clean_env_has_no_issues(checker, clean_envs):
    report = checker.check(clean_envs)
    assert isinstance(report, SecretsReport)
    assert not report.has_issues


def test_empty_sensitive_value_flagged(checker):
    envs = {"dev": {"API_KEY": ""}}
    report = checker.check(envs)
    assert report.has_issues
    assert any("empty" in i.reason for i in report.issues)


def test_placeholder_value_flagged(checker):
    envs = {"dev": {"SECRET_KEY": "changeme"}}
    report = checker.check(envs)
    assert report.has_issues
    assert any("placeholder" in i.reason for i in report.issues)


def test_low_entropy_value_flagged(checker):
    envs = {"dev": {"DB_PASSWORD": "aaaaaa"}}
    report = checker.check(envs)
    assert report.has_issues
    assert any("entropy" in i.reason for i in report.issues)


def test_issues_for_env_filters_correctly(checker):
    envs = {
        "dev": {"API_KEY": "changeme"},
        "prod": {"API_KEY": "xK9#mP2$qL7!nR4@vT6&wY1"},
    }
    report = checker.check(envs)
    assert len(report.issues_for_env("dev")) == 1
    assert len(report.issues_for_env("prod")) == 0


def test_secret_issue_str_masks_value():
    issue = SecretIssue("API_KEY", "supersecret", "placeholder", "dev")
    result = str(issue)
    assert "supe****" in result
    assert "supersecret" not in result


def test_report_env_names_captured(checker):
    envs = {"alpha": {"PORT": "8080"}, "beta": {"PORT": "9090"}}
    report = checker.check(envs)
    assert "alpha" in report.env_names
    assert "beta" in report.env_names
