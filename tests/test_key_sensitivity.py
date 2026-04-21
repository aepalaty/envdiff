"""Tests for key_sensitivity module."""
import pytest
from envdiff.key_sensitivity import (
    SensitivityCalculator,
    SensitivityEntry,
    SensitivityReport,
    _tier,
    _looks_plain,
)


@pytest.fixture
def calculator():
    return SensitivityCalculator()


@pytest.fixture
def three_envs():
    return {
        "prod": {
            "DB_PASSWORD": "s3cr3t!",
            "DB_HOST": "db.prod.internal",
            "APP_PORT": "8080",
            "SSL_CERT": "-----BEGIN CERT-----",
        },
        "staging": {
            "DB_PASSWORD": "CHANGEME",
            "DB_HOST": "db.staging.internal",
            "APP_PORT": "8080",
        },
        "dev": {
            "DB_PASSWORD": "devpass",
            "DB_HOST": "localhost",
            "APP_PORT": "5000",
            "API_KEY": "abc123",
        },
    }


def test_tier_critical_password():
    assert _tier("DB_PASSWORD") == "CRITICAL"


def test_tier_critical_token():
    assert _tier("AUTH_TOKEN") == "CRITICAL"


def test_tier_high_ssl_cert():
    assert _tier("SSL_CERT") == "HIGH"


def test_tier_medium_db_host():
    assert _tier("DB_HOST") == "MEDIUM"


def test_tier_low_app_port():
    assert _tier("APP_PORT") == "LOW"


def test_looks_plain_real_value():
    assert _looks_plain("s3cr3t!") is True


def test_looks_plain_placeholder_changeme():
    assert _looks_plain("CHANGEME") is False


def test_looks_plain_empty_string():
    assert _looks_plain("") is False


def test_looks_plain_angle_bracket_placeholder():
    assert _looks_plain("<YOUR_SECRET>") is False


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, SensitivityReport)


def test_all_keys_collected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    keys = {e.key for e in report.entries}
    assert "DB_PASSWORD" in keys
    assert "APP_PORT" in keys
    assert "API_KEY" in keys


def test_env_names_captured(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.env_names) == {"prod", "staging", "dev"}


def test_plain_secrets_detected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert report.has_plain_secrets()


def test_critical_entries_listed(calculator, three_envs):
    report = calculator.calculate(three_envs)
    critical_keys = {e.key for e in report.critical()}
    assert "DB_PASSWORD" in critical_keys
    assert "API_KEY" in critical_keys


def test_placeholder_not_flagged_as_plain(calculator, three_envs):
    report = calculator.calculate(three_envs)
    db_pass = next(e for e in report.entries if e.key == "DB_PASSWORD")
    assert "staging" not in db_pass.envs_with_plain_value


def test_real_value_flagged_as_plain(calculator, three_envs):
    report = calculator.calculate(three_envs)
    db_pass = next(e for e in report.entries if e.key == "DB_PASSWORD")
    assert "prod" in db_pass.envs_with_plain_value
    assert "dev" in db_pass.envs_with_plain_value


def test_no_plain_secrets_clean_env(calculator):
    envs = {"env": {"APP_NAME": "myapp", "LOG_LEVEL": "info"}}
    report = calculator.calculate(envs)
    assert not report.has_plain_secrets()
