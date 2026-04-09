"""Tests for EnvSchema loading and structure."""

import json
import pytest
from pathlib import Path

from envdiff.schema import EnvSchema, KeySchema


SCHEMA_DICT = {
    "allow_extra_keys": False,
    "keys": {
        "DATABASE_URL": {"required": True, "description": "Postgres connection string"},
        "DEBUG": {
            "required": False,
            "allowed_values": ["true", "false"],
        },
        "PORT": {"required": True, "pattern": r"\d+"},
    },
}


def test_schema_from_dict_parses_keys():
    schema = EnvSchema.from_dict(SCHEMA_DICT)
    assert "DATABASE_URL" in schema.keys
    assert "DEBUG" in schema.keys
    assert "PORT" in schema.keys


def test_schema_required_keys():
    schema = EnvSchema.from_dict(SCHEMA_DICT)
    assert set(schema.required_keys()) == {"DATABASE_URL", "PORT"}


def test_schema_optional_keys():
    schema = EnvSchema.from_dict(SCHEMA_DICT)
    assert schema.optional_keys() == ["DEBUG"]


def test_schema_allow_extra_keys_flag():
    schema = EnvSchema.from_dict(SCHEMA_DICT)
    assert schema.allow_extra_keys is False


def test_key_schema_allowed_values():
    schema = EnvSchema.from_dict(SCHEMA_DICT)
    debug = schema.keys["DEBUG"]
    assert debug.allowed_values == ["true", "false"]
    assert debug.required is False


def test_key_schema_pattern():
    schema = EnvSchema.from_dict(SCHEMA_DICT)
    port = schema.keys["PORT"]
    assert port.pattern == r"\d+"


def test_schema_load_from_file(tmp_path: Path):
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(SCHEMA_DICT))
    schema = EnvSchema.load(schema_file)
    assert set(schema.required_keys()) == {"DATABASE_URL", "PORT"}
