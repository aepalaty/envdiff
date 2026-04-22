"""Tests for key_checksum module."""
import pytest
from envdiff.key_checksum import (
    ChecksumCalculator,
    ChecksumReport,
    ChecksumMismatch,
    _hash_value,
)
from envdiff.checksum_formatter import ChecksumFormatter


@pytest.fixture
def calculator():
    return ChecksumCalculator()


@pytest.fixture
def three_envs():
    return {
        "dev": {"DB_URL": "postgres://localhost/dev", "PORT": "5432", "DEBUG": "true"},
        "staging": {"DB_URL": "postgres://staging/app", "PORT": "5432", "DEBUG": "false"},
        "prod": {"DB_URL": "postgres://prod/app", "PORT": "5432", "SECRET": "abc123"},
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, ChecksumReport)


def test_env_names_captured(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_all_keys_collected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.entries.keys()) == {"DB_URL", "PORT", "DEBUG", "SECRET"}


def test_port_has_no_mismatch(calculator, three_envs):
    report = calculator.calculate(three_envs)
    port_entries = report.entries["PORT"]
    hashes = {e.value_hash for e in port_entries}
    assert len(hashes) == 1


def test_db_url_has_mismatch(calculator, three_envs):
    report = calculator.calculate(three_envs)
    mismatches = report.mismatches()
    mismatch_keys = [m.key for m in mismatches]
    assert "DB_URL" in mismatch_keys


def test_has_mismatches_true(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert report.has_mismatches() is True


def test_has_mismatches_false(calculator):
    envs = {
        "a": {"KEY": "same_value"},
        "b": {"KEY": "same_value"},
    }
    report = calculator.calculate(envs)
    assert report.has_mismatches() is False


def test_checksum_for_returns_hash(calculator, three_envs):
    report = calculator.calculate(three_envs)
    result = report.checksum_for("PORT", "dev")
    assert result == _hash_value("5432")


def test_checksum_for_missing_key_returns_none(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert report.checksum_for("NONEXISTENT", "dev") is None


def test_mismatch_str(calculator, three_envs):
    report = calculator.calculate(three_envs)
    mismatches = report.mismatches()
    db_mismatch = next(m for m in mismatches if m.key == "DB_URL")
    s = str(db_mismatch)
    assert "DB_URL" in s
    assert "distinct" in s


def test_formatter_clean_report():
    envs = {"a": {"KEY": "value"}, "b": {"KEY": "value"}}
    calc = ChecksumCalculator()
    report = calc.calculate(envs)
    fmt = ChecksumFormatter(use_color=False)
    output = fmt.format_report(report)
    assert "All checksums match" in output


def test_formatter_mismatch_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    fmt = ChecksumFormatter(use_color=False)
    output = fmt.format_report(report)
    assert "mismatch" in output.lower()
    assert "DB_URL" in output


def test_formatter_show_clean_includes_matching_keys(calculator, three_envs):
    report = calculator.calculate(three_envs)
    fmt = ChecksumFormatter(use_color=False)
    output = fmt.format_report(report, show_clean=True)
    assert "matching checksums" in output
