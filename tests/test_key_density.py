"""Tests for envdiff.key_density."""
import pytest
from envdiff.key_density import DensityCalculator, DensityEntry, DensityReport


@pytest.fixture
def calculator():
    return DensityCalculator()


@pytest.fixture
def three_envs():
    return {
        "dev": {"DB_URL": "postgres://localhost", "API_KEY": "dev-key", "DEBUG": "true"},
        "staging": {"DB_URL": "postgres://staging", "API_KEY": "", "SECRET": "abc"},
        "prod": {"DB_URL": "postgres://prod", "SECRET": "xyz"},
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, DensityReport)


def test_env_names_captured(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_all_keys_collected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    keys = {e.key for e in report.entries}
    assert keys == {"DB_URL", "API_KEY", "DEBUG", "SECRET"}


def test_db_url_fully_populated(calculator, three_envs):
    report = calculator.calculate(three_envs)
    entry = report.entry_for("DB_URL")
    assert entry is not None
    assert entry.populated_count == 3
    assert entry.density_ratio == 1.0
    assert not entry.is_sparse


def test_debug_is_sparse(calculator, three_envs):
    report = calculator.calculate(three_envs)
    entry = report.entry_for("DEBUG")
    assert entry is not None
    assert entry.populated_count == 1
    assert entry.missing_count == 2
    assert entry.is_sparse


def test_api_key_counts_empty_separately(calculator, three_envs):
    report = calculator.calculate(three_envs)
    entry = report.entry_for("API_KEY")
    assert entry is not None
    assert entry.populated_count == 1
    assert entry.empty_count == 1
    assert entry.missing_count == 1


def test_sparse_keys_list(calculator, three_envs):
    report = calculator.calculate(three_envs)
    sparse = {e.key for e in report.sparse_keys}
    assert "DEBUG" in sparse
    assert "DB_URL" not in sparse


def test_fully_populated_keys(calculator, three_envs):
    report = calculator.calculate(three_envs)
    full = {e.key for e in report.fully_populated_keys}
    assert "DB_URL" in full
    assert "DEBUG" not in full


def test_density_ratio_bounds(calculator, three_envs):
    report = calculator.calculate(three_envs)
    for entry in report.entries:
        assert 0.0 <= entry.density_ratio <= 1.0


def test_str_representation(calculator, three_envs):
    report = calculator.calculate(three_envs)
    entry = report.entry_for("DB_URL")
    s = str(entry)
    assert "DB_URL" in s
    assert "100%" in s


def test_empty_envs_returns_empty_report(calculator):
    report = calculator.calculate({})
    assert report.entries == []
    assert report.env_names == []
