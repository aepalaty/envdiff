import pytest
from envdiff.key_balance import BalanceCalculator, BalanceReport, BalanceEntry
from envdiff.balance_formatter import BalanceFormatter


@pytest.fixture
def calculator():
    return BalanceCalculator()


@pytest.fixture
def three_envs():
    return {
        "dev": {"DB_URL": "localhost", "APP_NAME": "myapp", "DEBUG": "true"},
        "staging": {"DB_URL": "staging-db", "APP_NAME": "myapp"},
        "prod": {"DB_URL": "prod-db", "APP_NAME": "myapp", "SECRET_KEY": "abc123"},
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, BalanceReport)


def test_env_names_captured(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_all_keys_collected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    keys = {e.key for e in report.entries}
    assert keys == {"DB_URL", "APP_NAME", "DEBUG", "SECRET_KEY"}


def test_universal_key_is_balanced(calculator, three_envs):
    report = calculator.calculate(three_envs)
    db_entry = next(e for e in report.entries if e.key == "DB_URL")
    assert db_entry.is_balanced
    assert db_entry.balance_ratio == 1.0


def test_partial_key_is_unbalanced(calculator, three_envs):
    report = calculator.calculate(three_envs)
    debug_entry = next(e for e in report.entries if e.key == "DEBUG")
    assert not debug_entry.is_balanced
    assert "staging" in debug_entry.absent_from
    assert "prod" in debug_entry.absent_from


def test_has_imbalance_when_keys_missing(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert report.has_imbalance


def test_no_imbalance_when_all_keys_present(calculator):
    envs = {
        "dev": {"KEY": "val1"},
        "prod": {"KEY": "val2"},
    }
    report = calculator.calculate(envs)
    assert not report.has_imbalance


def test_average_balance_below_one_when_missing(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert report.average_balance < 1.0


def test_average_balance_is_one_for_perfect_envs(calculator):
    envs = {
        "a": {"X": "1", "Y": "2"},
        "b": {"X": "3", "Y": "4"},
    }
    report = calculator.calculate(envs)
    assert report.average_balance == 1.0


def test_formatter_includes_env_names(three_envs):
    calc = BalanceCalculator()
    report = calc.calculate(three_envs)
    formatter = BalanceFormatter(color=False)
    output = formatter.format_report(report)
    assert "dev" in output
    assert "staging" in output
    assert "prod" in output


def test_formatter_includes_all_keys(three_envs):
    calc = BalanceCalculator()
    report = calc.calculate(three_envs)
    formatter = BalanceFormatter(color=False)
    output = formatter.format_report(report)
    assert "DB_URL" in output
    assert "DEBUG" in output
    assert "SECRET_KEY" in output


def test_formatter_reports_imbalance(three_envs):
    calc = BalanceCalculator()
    report = calc.calculate(three_envs)
    formatter = BalanceFormatter(color=False)
    output = formatter.format_report(report)
    assert "not fully balanced" in output


def test_formatter_reports_all_balanced():
    calc = BalanceCalculator()
    envs = {"a": {"K": "1"}, "b": {"K": "2"}}
    report = calc.calculate(envs)
    formatter = BalanceFormatter(color=False)
    output = formatter.format_report(report)
    assert "All keys are balanced" in output
