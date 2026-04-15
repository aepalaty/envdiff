"""Tests for envdiff.key_pattern and envdiff.pattern_formatter."""
import pytest

from envdiff.key_pattern import KeyPatternChecker, PatternReport, BUILTIN_PATTERNS
from envdiff.pattern_formatter import PatternFormatter


@pytest.fixture()
def checker():
    return KeyPatternChecker(
        rules={
            "APP_URL": "url",
            "PORT": "port",
            "RELEASE": "semver",
            "REQUEST_ID": "uuid",
        }
    )


@pytest.fixture()
def formatter():
    return PatternFormatter(color=False)


VALID_ENV = {
    "APP_URL": "https://example.com",
    "PORT": "8080",
    "RELEASE": "1.2.3",
    "REQUEST_ID": "550e8400-e29b-41d4-a716-446655440000",
}


def test_valid_env_has_no_violations(checker):
    report = checker.check(VALID_ENV, env_name="prod")
    assert not report.has_violations
    assert report.violation_keys == []


def test_invalid_url_detected(checker):
    env = {**VALID_ENV, "APP_URL": "not-a-url"}
    report = checker.check(env, env_name="dev")
    assert report.has_violations
    assert "APP_URL" in report.violation_keys


def test_invalid_port_detected(checker):
    env = {**VALID_ENV, "PORT": "abc"}
    report = checker.check(env, env_name="dev")
    assert "PORT" in report.violation_keys


def test_invalid_semver_detected(checker):
    env = {**VALID_ENV, "RELEASE": "v1.2"}
    report = checker.check(env, env_name="dev")
    assert "RELEASE" in report.violation_keys


def test_missing_key_is_skipped(checker):
    # PORT is not in env — should not produce a violation
    env = {"APP_URL": "https://ok.com"}
    report = checker.check(env, env_name="ci")
    assert "PORT" not in report.violation_keys


def test_check_all_returns_one_report_per_env(checker):
    envs = {"prod": VALID_ENV, "dev": {**VALID_ENV, "PORT": "bad"}}
    reports = checker.check_all(envs)
    assert set(reports.keys()) == {"prod", "dev"}
    assert not reports["prod"].has_violations
    assert reports["dev"].has_violations


def test_custom_extra_pattern():
    checker = KeyPatternChecker(
        rules={"COLOR": "hex_color"},
        extra_patterns={"hex_color": r"^#[0-9a-fA-F]{6}$"},
    )
    good = checker.check({"COLOR": "#ff0000"}, env_name="ui")
    bad = checker.check({"COLOR": "red"}, env_name="ui")
    assert not good.has_violations
    assert bad.has_violations


def test_unknown_pattern_name_does_not_crash(checker):
    c = KeyPatternChecker(rules={"KEY": "nonexistent_pattern"})
    report = c.check({"KEY": "anything"}, env_name="test")
    assert not report.has_violations


def test_formatter_clean_report(formatter):
    report = PatternReport(env_name="prod")
    output = formatter.format_report(report)
    assert "prod" in output
    assert "passed" in output


def test_formatter_shows_violation(formatter):
    checker = KeyPatternChecker(rules={"PORT": "port"})
    report = checker.check({"PORT": "not-a-port"}, env_name="staging")
    output = formatter.format_report(report)
    assert "PORT" in output
    assert "port" in output


def test_formatter_summary_no_violations(formatter):
    reports = {"prod": PatternReport(env_name="prod")}
    summary = formatter.format_summary(reports)
    assert "no violations" in summary


def test_formatter_summary_counts_violations(formatter):
    checker = KeyPatternChecker(rules={"PORT": "port", "URL": "url"})
    env = {"PORT": "bad", "URL": "bad"}
    reports = {"dev": checker.check(env, env_name="dev")}
    summary = formatter.format_summary(reports)
    assert "2" in summary
