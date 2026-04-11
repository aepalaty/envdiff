"""Tests for key_deprecation module."""

import pytest
from envdiff.key_deprecation import DeprecationEntry, DeprecationRegistry, DeprecationReport


@pytest.fixture
def registry():
    return DeprecationRegistry(
        entries=[
            {"key": "OLD_DB_URL", "reason": "Use DATABASE_URL", "replacement": "DATABASE_URL"},
            {"key": "SECRET", "reason": "Too generic"},
        ]
    )


def test_no_deprecated_keys_returns_clean_report(registry):
    env = {"DATABASE_URL": "postgres://localhost/db", "API_KEY": "abc123"}
    report = registry.check(env)
    assert not report.has_deprecated
    assert report.deprecated_keys == []


def test_detects_deprecated_key(registry):
    env = {"OLD_DB_URL": "postgres://localhost/old", "PORT": "5432"}
    report = registry.check(env)
    assert report.has_deprecated
    assert "OLD_DB_URL" in report.deprecated_keys


def test_detects_multiple_deprecated_keys(registry):
    env = {"OLD_DB_URL": "val", "SECRET": "shh", "SAFE_KEY": "ok"}
    report = registry.check(env)
    assert len(report.hits) == 2


def test_replacement_shown_in_str():
    entry = DeprecationEntry(key="OLD", reason="Replaced", replacement="NEW")
    assert "NEW" in str(entry)
    assert "OLD" in str(entry)


def test_no_replacement_str_omits_use_clause():
    entry = DeprecationEntry(key="SECRET", reason="Too generic")
    assert "use" not in str(entry).lower()


def test_report_str_lists_hits(registry):
    env = {"OLD_DB_URL": "val"}
    report = registry.check(env)
    output = str(report)
    assert "OLD_DB_URL" in output
    assert "Deprecated" in output


def test_empty_report_str():
    report = DeprecationReport()
    assert "No deprecated" in str(report)


def test_register_adds_entry():
    reg = DeprecationRegistry()
    reg.register("LEGACY_KEY", reason="Old pattern", replacement="NEW_KEY")
    env = {"LEGACY_KEY": "value"}
    report = reg.check(env)
    assert report.has_deprecated


def test_from_dict_parses_entries():
    data = {
        "deprecated": [
            {"key": "MYSQL_PASS", "reason": "Use MYSQL_PASSWORD", "replacement": "MYSQL_PASSWORD"}
        ]
    }
    reg = DeprecationRegistry.from_dict(data)
    assert "MYSQL_PASS" in reg._registry


def test_from_dict_empty_data():
    reg = DeprecationRegistry.from_dict({})
    assert len(reg._registry) == 0
