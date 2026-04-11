"""Tests for envdiff.key_aliases."""

import pytest
from envdiff.key_aliases import AliasMatch, AliasReport, KeyAliasDetector


@pytest.fixture
def detector() -> KeyAliasDetector:
    return KeyAliasDetector()


@pytest.fixture
def env_a() -> dict:
    return {
        "DATABASE_URL": "postgres://localhost/app",
        "SECRET_KEY": "abc123",
        "PORT": "8080",
    }


@pytest.fixture
def env_b() -> dict:
    return {
        "DB_URL": "postgres://localhost/app",
        "APP_SECRET": "abc123",
        "PORT": "8080",
    }


def test_detects_database_url_alias(detector, env_a, env_b):
    report = detector.detect(env_a, env_b)
    keys = {(m.key_a, m.key_b) for m in report.matches}
    assert ("DATABASE_URL", "DB_URL") in keys


def test_detects_secret_key_alias(detector, env_a, env_b):
    report = detector.detect(env_a, env_b)
    keys = {(m.key_a, m.key_b) for m in report.matches}
    assert ("SECRET_KEY", "APP_SECRET") in keys


def test_shared_keys_not_reported_as_aliases(detector, env_a, env_b):
    report = detector.detect(env_a, env_b)
    all_keys = {m.key_a for m in report.matches} | {m.key_b for m in report.matches}
    assert "PORT" not in all_keys


def test_has_aliases_true_when_matches_found(detector, env_a, env_b):
    report = detector.detect(env_a, env_b)
    assert report.has_aliases is True


def test_has_aliases_false_when_identical(detector):
    env = {"FOO": "bar", "BAZ": "qux"}
    report = detector.detect(env, env)
    assert report.has_aliases is False


def test_unresolved_keys_reported(detector):
    env_a = {"UNKNOWN_KEY_X": "val1"}
    env_b = {"UNKNOWN_KEY_Y": "val2"}
    report = detector.detect(env_a, env_b)
    assert "UNKNOWN_KEY_X" in report.unresolved_a
    assert "UNKNOWN_KEY_Y" in report.unresolved_b


def test_no_false_positives_for_unrelated_keys(detector):
    env_a = {"ALPHA": "1", "BETA": "2"}
    env_b = {"GAMMA": "3", "DELTA": "4"}
    report = detector.detect(env_a, env_b)
    assert report.has_aliases is False
    assert len(report.unresolved_a) == 2
    assert len(report.unresolved_b) == 2


def test_custom_alias_group_detected():
    extra = [("MY_TOKEN", "APP_TOKEN")]
    detector = KeyAliasDetector(extra_groups=extra)
    env_a = {"MY_TOKEN": "tok_abc"}
    env_b = {"APP_TOKEN": "tok_abc"}
    report = detector.detect(env_a, env_b)
    assert report.has_aliases is True
    assert report.matches[0].key_a == "MY_TOKEN"
    assert report.matches[0].key_b == "APP_TOKEN"


def test_alias_match_str():
    group = ("DATABASE_URL", "DB_URL")
    match = AliasMatch(key_a="DATABASE_URL", key_b="DB_URL", group=group)
    result = str(match)
    assert "DATABASE_URL" in result
    assert "DB_URL" in result


def test_summary_lists_matches(detector, env_a, env_b):
    report = detector.detect(env_a, env_b)
    summary = report.summary()
    assert "alias pair" in summary
    assert "DATABASE_URL" in summary or "DB_URL" in summary


def test_summary_no_aliases():
    report = AliasReport()
    assert "No alias pairs" in report.summary()
