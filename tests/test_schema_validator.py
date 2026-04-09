"""Tests for SchemaValidator."""

import pytest

from envdiff.schema import EnvSchema
from envdiff.schema_validator import SchemaValidator


SCHEMA_DICT = {
    "allow_extra_keys": False,
    "keys": {
        "DATABASE_URL": {"required": True},
        "DEBUG": {"required": False, "allowed_values": ["true", "false"]},
        "PORT": {"required": True, "pattern": r"\d+"},
    },
}


@pytest.fixture
def schema():
    return EnvSchema.from_dict(SCHEMA_DICT)


@pytest.fixture
def validator(schema):
    return SchemaValidator(schema)


def test_valid_env_passes(validator):
    env = {"DATABASE_URL": "postgres://localhost/db", "DEBUG": "true", "PORT": "5432"}
    result = validator.validate(env)
    assert result.is_valid
    assert str(result) == "Schema validation passed."


def test_missing_required_key(validator):
    env = {"DEBUG": "true", "PORT": "5432"}
    result = validator.validate(env)
    assert not result.is_valid
    assert "DATABASE_URL" in result.missing_required


def test_disallowed_value_flagged(validator):
    env = {"DATABASE_URL": "postgres://localhost/db", "DEBUG": "yes", "PORT": "5432"}
    result = validator.validate(env)
    assert not result.is_valid
    assert "DEBUG" in result.disallowed_values
    assert result.disallowed_values["DEBUG"] == "yes"


def test_pattern_violation_flagged(validator):
    env = {"DATABASE_URL": "postgres://localhost/db", "PORT": "not-a-port"}
    result = validator.validate(env)
    assert not result.is_valid
    assert "PORT" in result.pattern_violations


def test_extra_keys_flagged_when_not_allowed(validator):
    env = {
        "DATABASE_URL": "postgres://localhost/db",
        "PORT": "5432",
        "UNKNOWN_KEY": "value",
    }
    result = validator.validate(env)
    assert not result.is_valid
    assert "UNKNOWN_KEY" in result.extra_keys


def test_extra_keys_allowed_when_flag_set():
    schema = EnvSchema.from_dict({**SCHEMA_DICT, "allow_extra_keys": True})
    validator = SchemaValidator(schema)
    env = {"DATABASE_URL": "postgres://localhost/db", "PORT": "5432", "EXTRA": "val"}
    result = validator.validate(env)
    assert result.is_valid


def test_str_output_contains_violations(validator):
    env = {"PORT": "bad", "DEBUG": "maybe"}
    result = validator.validate(env)
    output = str(result)
    assert "DATABASE_URL" in output
    assert "DEBUG" in output
    assert "PORT" in output
