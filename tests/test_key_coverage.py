import pytest
from envdiff.key_coverage import CoverageCalculator, CoverageEntry, CoverageReport


@pytest.fixture
def calculator():
    return CoverageCalculator()


@pytest.fixture
def three_envs():
    return {
        "dev": {"DB_URL": "dev-db", "SECRET": "abc", "DEBUG": "true"},
        "staging": {"DB_URL": "stg-db", "SECRET": "xyz"},
        "prod": {"DB_URL": "prod-db"},
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, CoverageReport)


def test_all_keys_collected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    keys = {e.key for e in report.entries}
    assert keys == {"DB_URL", "SECRET", "DEBUG"}


def test_universal_key_has_full_coverage(calculator, three_envs):
    report = calculator.calculate(three_envs)
    db_entry = next(e for e in report.entries if e.key == "DB_URL")
    assert db_entry.is_universal
    assert db_entry.coverage_ratio == 1.0


def test_partial_key_has_correct_absent(calculator, three_envs):
    report = calculator.calculate(three_envs)
    debug_entry = next(e for e in report.entries if e.key == "DEBUG")
    assert not debug_entry.is_universal
    assert "staging" in debug_entry.absent_from
    assert "prod" in debug_entry.absent_from
    assert "dev" not in debug_entry.absent_from


def test_coverage_ratio_calculation(calculator, three_envs):
    report = calculator.calculate(three_envs)
    secret_entry = next(e for e in report.entries if e.key == "SECRET")
    assert abs(secret_entry.coverage_ratio - 2 / 3) < 0.01


def test_universal_keys_list(calculator, three_envs):
    report = calculator.calculate(three_envs)
    universal = report.universal_keys
    assert len(universal) == 1
    assert universal[0].key == "DB_URL"


def test_partial_keys_list(calculator, three_envs):
    report = calculator.calculate(three_envs)
    partial = report.partial_keys
    partial_key_names = {e.key for e in partial}
    assert "SECRET" in partial_key_names
    assert "DEBUG" in partial_key_names


def test_average_coverage(calculator, three_envs):
    report = calculator.calculate(three_envs)
    # DB_URL=1.0, SECRET=2/3, DEBUG=1/3 -> avg = 2/3
    assert abs(report.average_coverage - 2 / 3) < 0.01


def test_env_names_captured(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_entry_str(calculator, three_envs):
    report = calculator.calculate(three_envs)
    db_entry = next(e for e in report.entries if e.key == "DB_URL")
    s = str(db_entry)
    assert "DB_URL" in s
    assert "100%" in s
