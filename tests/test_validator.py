"""Tests for the EnvValidator module."""

import pytest
from envdiff.validator import EnvValidator, ValidationResult


@pytest.fixture
def sample_env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "SECRET_KEY": "supersecret",
        "DEBUG": "true",
        "PORT": "8080",
    }


def test_valid_env_passes(sample_env):
    validator = EnvValidator(required_keys=["DATABASE_URL", "SECRET_KEY"])
    result = validator.validate(sample_env)
    assert result.is_valid
    assert result.missing_required == []


def test_missing_required_keys():
    env = {"DEBUG": "true"}
    validator = EnvValidator(required_keys=["DATABASE_URL", "SECRET_KEY", "DEBUG"])
    result = validator.validate(env)
    assert not result.is_valid
    assert "DATABASE_URL" in result.missing_required
    assert "SECRET_KEY" in result.missing_required
    assert "DEBUG" not in result.missing_required


def test_unknown_keys_flagged_when_not_allowed(sample_env):
    validator = EnvValidator(
        required_keys=["DATABASE_URL", "SECRET_KEY"],
        optional_keys=["DEBUG"],
        allow_unknown=False,
    )
    result = validator.validate(sample_env)
    assert "PORT" in result.unknown_keys
    assert "DEBUG" not in result.unknown_keys


def test_unknown_keys_allowed_by_default(sample_env):
    validator = EnvValidator(required_keys=["DATABASE_URL"])
    result = validator.validate(sample_env)
    assert result.unknown_keys == []


def test_empty_values_detected():
    env = {"API_KEY": "", "HOST": "localhost", "TOKEN": None}
    validator = EnvValidator(required_keys=["API_KEY", "HOST"], warn_empty=True)
    result = validator.validate(env)
    assert "API_KEY" in result.empty_values
    assert "TOKEN" in result.empty_values
    assert "HOST" not in result.empty_values


def test_empty_values_ignored_when_disabled():
    env = {"API_KEY": "", "HOST": "localhost"}
    validator = EnvValidator(required_keys=["API_KEY", "HOST"], warn_empty=False)
    result = validator.validate(env)
    assert result.empty_values == []


def test_validation_result_str_all_issues():
    result = ValidationResult(
        missing_required=["SECRET_KEY"],
        unknown_keys=["EXTRA_VAR"],
        empty_values=["API_KEY"],
    )
    output = str(result)
    assert "Missing required keys" in output
    assert "Unknown keys" in output
    assert "empty values" in output


def test_validation_result_str_no_issues():
    result = ValidationResult()
    assert str(result) == "Validation passed."
