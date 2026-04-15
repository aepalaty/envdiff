"""Tests for key_casing module."""
import pytest
from envdiff.key_casing import CasingChecker, CasingReport, _detect_convention
from envdiff.casing_formatter import CasingFormatter


@pytest.fixture
def checker():
    return CasingChecker()


@pytest.fixture
def three_envs():
    return {
        "prod": {"DB_HOST": "prod-db", "DB_PORT": "5432", "API_KEY": "secret"},
        "staging": {"DB_HOST": "stage-db", "DB_PORT": "5433", "debug_mode": "true"},
        "dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "apiKey": "dev-key"},
    }


def test_detect_screaming_snake():
    assert _detect_convention("DB_HOST") == "SCREAMING_SNAKE"
    assert _detect_convention("API_KEY_SECRET") == "SCREAMING_SNAKE"


def test_detect_snake_case():
    assert _detect_convention("debug_mode") == "snake_case"


def test_detect_camel_case():
    assert _detect_convention("apiKey") == "camelCase"


def test_detect_pascal_case():
    assert _detect_convention("ApiKey") == "PascalCase"


def test_detect_kebab_case():
    assert _detect_convention("api-key") == "kebab-case"


def test_calculate_returns_report(checker, three_envs):
    report = checker.calculate(three_envs)
    assert isinstance(report, CasingReport)


def test_env_names_captured(checker, three_envs):
    report = checker.calculate(three_envs)
    assert set(report.env_names) == {"prod", "staging", "dev"}


def test_dominant_convention_is_screaming_snake(checker, three_envs):
    report = checker.calculate(three_envs)
    assert report.dominant_convention == "SCREAMING_SNAKE"


def test_mixed_casing_detected(checker, three_envs):
    report = checker.calculate(three_envs)
    assert report.has_issues
    issue_keys = [i.key for i in report.issues]
    assert "debug_mode" in issue_keys
    assert "apiKey" in issue_keys


def test_clean_env_has_no_issues(checker):
    envs = {
        "prod": {"DB_HOST": "prod-db", "API_KEY": "secret"},
        "dev": {"DB_HOST": "localhost", "API_KEY": "dev-key"},
    }
    report = checker.calculate(envs)
    assert not report.has_issues


def test_explicit_convention_overrides_dominant(checker):
    envs = {
        "prod": {"DB_HOST": "prod-db", "apiKey": "secret"},
    }
    report = checker.calculate(envs, expected_convention="camelCase")
    assert report.dominant_convention == "camelCase"
    issue_keys = [i.key for i in report.issues]
    assert "DB_HOST" in issue_keys
    assert "apiKey" not in issue_keys


def test_issues_for_env_filters_correctly(checker, three_envs):
    report = checker.calculate(three_envs)
    dev_issues = report.issues_for_env("dev")
    assert all(i.env_name == "dev" for i in dev_issues)


def test_formatter_clean_report():
    formatter = CasingFormatter(color=False)
    report = CasingReport(
        env_names=["prod"],
        issues=[],
        dominant_convention="SCREAMING_SNAKE",
    )
    output = formatter.format_report(report)
    assert "consistent" in output
    assert "SCREAMING_SNAKE" in output


def test_formatter_shows_issues(checker, three_envs):
    formatter = CasingFormatter(color=False)
    report = checker.calculate(three_envs)
    output = formatter.format_report(report)
    assert "debug_mode" in output
    assert "apiKey" in output


def test_formatter_summary_ok():
    formatter = CasingFormatter(color=False)
    report = CasingReport(env_names=["prod"], issues=[], dominant_convention="SCREAMING_SNAKE")
    assert "OK" in formatter.format_summary(report)


def test_formatter_summary_with_issues(checker, three_envs):
    formatter = CasingFormatter(color=False)
    report = checker.calculate(three_envs)
    summary = formatter.format_summary(report)
    assert "issue" in summary
