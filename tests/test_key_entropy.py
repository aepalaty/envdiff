"""Tests for envdiff.key_entropy."""

import pytest

from envdiff.key_entropy import (
    EntropyCalculator,
    EntropyEntry,
    EntropyReport,
    _shannon_entropy,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def calculator() -> EntropyCalculator:
    return EntropyCalculator(threshold=2.5)


@pytest.fixture()
def sample_env() -> dict:
    return {
        "SECRET_KEY": "changeme",          # low entropy
        "DATABASE_URL": "postgres://user:s3cR3t!xYz@localhost/db",  # high entropy
        "DEBUG": "true",                   # low entropy
        "API_TOKEN": "aB3$kL9#mNpQrSt2",   # high entropy
        "EMPTY_KEY": "",                   # empty – not flagged as weak
    }


# ---------------------------------------------------------------------------
# Unit tests for _shannon_entropy
# ---------------------------------------------------------------------------


def test_entropy_empty_string_is_zero():
    assert _shannon_entropy("") == 0.0


def test_entropy_single_char_is_zero():
    assert _shannon_entropy("aaaa") == pytest.approx(0.0, abs=1e-9)


def test_entropy_increases_with_variety():
    low = _shannon_entropy("aaaa")
    high = _shannon_entropy("abcd")
    assert high > low


# ---------------------------------------------------------------------------
# EntropyCalculator.calculate
# ---------------------------------------------------------------------------


def test_calculate_returns_report(calculator, sample_env):
    report = calculator.calculate(sample_env, "production")
    assert isinstance(report, EntropyReport)
    assert report.env_name == "production"


def test_all_keys_present_in_report(calculator, sample_env):
    report = calculator.calculate(sample_env)
    keys = {e.key for e in report.entries}
    assert keys == set(sample_env.keys())


def test_low_entropy_value_flagged_as_weak(calculator, sample_env):
    report = calculator.calculate(sample_env)
    weak_keys = {e.key for e in report.weak_keys}
    assert "SECRET_KEY" in weak_keys
    assert "DEBUG" in weak_keys


def test_high_entropy_value_not_flagged(calculator, sample_env):
    report = calculator.calculate(sample_env)
    ok_keys = {e.key for e in report.entries if not e.is_weak}
    assert "DATABASE_URL" in ok_keys
    assert "API_TOKEN" in ok_keys


def test_empty_value_not_flagged_as_weak(calculator, sample_env):
    report = calculator.calculate(sample_env)
    empty_entry = next(e for e in report.entries if e.key == "EMPTY_KEY")
    assert not empty_entry.is_weak


def test_has_weak_values_true_when_weak_keys_present(calculator, sample_env):
    report = calculator.calculate(sample_env)
    assert report.has_weak_values is True


def test_has_weak_values_false_for_clean_env(calculator):
    strong = {"TOKEN": "aB3$kL9#mNpQrSt2uVwXyZ"}
    report = calculator.calculate(strong)
    assert report.has_weak_values is False


def test_summary_contains_env_name(calculator, sample_env):
    report = calculator.calculate(sample_env, "staging")
    assert "staging" in report.summary()


def test_calculate_all_returns_dict_keyed_by_name(calculator, sample_env):
    envs = {"prod": sample_env, "dev": {"X": "abc123"}}
    reports = calculator.calculate_all(envs)
    assert set(reports.keys()) == {"prod", "dev"}
    assert all(isinstance(r, EntropyReport) for r in reports.values())


def test_entry_str_shows_status():
    entry = EntropyEntry(key="FOO", value="bar", entropy=1.2, is_weak=True)
    assert "WEAK" in str(entry)
    entry_ok = EntropyEntry(key="BAZ", value="xYz!9", entropy=3.1, is_weak=False)
    assert "ok" in str(entry_ok)
