"""Tests for envdiff.redactor."""

import pytest
from envdiff.redactor import Redactor, DEFAULT_MASK


@pytest.fixture
def redactor() -> Redactor:
    return Redactor()


def test_auto_detect_password_key(redactor):
    assert redactor.is_sensitive("DB_PASSWORD") is True


def test_auto_detect_token_key(redactor):
    assert redactor.is_sensitive("GITHUB_TOKEN") is True


def test_auto_detect_api_key(redactor):
    assert redactor.is_sensitive("STRIPE_API_KEY") is True


def test_non_sensitive_key(redactor):
    assert redactor.is_sensitive("APP_ENV") is False


def test_explicit_sensitive_key():
    r = Redactor(sensitive_keys=frozenset({"MY_CUSTOM_KEY"}))
    assert r.is_sensitive("MY_CUSTOM_KEY") is True


def test_redact_returns_mask_for_sensitive(redactor):
    assert redactor.redact("DB_PASSWORD", "s3cr3t") == DEFAULT_MASK


def test_redact_returns_value_for_safe(redactor):
    assert redactor.redact("APP_ENV", "production") == "production"


def test_redact_env_masks_sensitive_keys(redactor):
    env = {"APP_ENV": "production", "DB_PASSWORD": "s3cr3t", "PORT": "8080"}
    result = redactor.redact_env(env)
    assert result["APP_ENV"] == "production"
    assert result["DB_PASSWORD"] == DEFAULT_MASK
    assert result["PORT"] == "8080"


def test_custom_mask():
    r = Redactor(mask="[REDACTED]")
    assert r.redact("API_SECRET", "abc123") == "[REDACTED]"


def test_auto_detect_disabled():
    r = Redactor(auto_detect=False)
    assert r.is_sensitive("DB_PASSWORD") is False


def test_auto_detect_disabled_explicit_key_still_sensitive():
    r = Redactor(sensitive_keys=frozenset({"DB_PASSWORD"}), auto_detect=False)
    assert r.is_sensitive("DB_PASSWORD") is True
