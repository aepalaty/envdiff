import pytest
from envdiff.key_frequency import KeyFrequencyCalculator, FrequencyReport, FrequencyEntry
from envdiff.frequency_formatter import FrequencyFormatter


@pytest.fixture
def calculator():
    return KeyFrequencyCalculator()


@pytest.fixture
def three_envs():
    return {
        "prod": {"DB_URL": "postgres://prod", "SECRET_KEY": "abc", "REDIS_URL": "redis://prod"},
        "staging": {"DB_URL": "postgres://staging", "SECRET_KEY": "def", "DEBUG": "false"},
        "dev": {"DB_URL": "postgres://dev", "DEBUG": "true", "LOCAL_ONLY": "yes"},
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, FrequencyReport)
    assert report.total_envs == 3


def test_all_keys_collected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    keys = {e.key for e in report.entries}
    assert keys == {"DB_URL", "SECRET_KEY", "REDIS_URL", "DEBUG", "LOCAL_ONLY"}


def test_universal_key_in_all_envs(calculator, three_envs):
    report = calculator.calculate(three_envs)
    universal = {e.key for e in report.universal_keys()}
    assert "DB_URL" in universal


def test_unique_key_in_one_env(calculator, three_envs):
    report = calculator.calculate(three_envs)
    unique = {e.key for e in report.unique_keys()}
    assert "REDIS_URL" in unique
    assert "LOCAL_ONLY" in unique


def test_most_common_returns_sorted(calculator, three_envs):
    report = calculator.calculate(three_envs)
    top = report.most_common(3)
    assert top[0].key == "DB_URL"
    assert top[0].count == 3


def test_least_common_returns_sorted(calculator, three_envs):
    report = calculator.calculate(three_envs)
    bottom = report.least_common(2)
    assert all(e.count == 1 for e in bottom)


def test_frequency_entry_str(calculator, three_envs):
    report = calculator.calculate(three_envs)
    entry = next(e for e in report.entries if e.key == "DB_URL")
    result = str(entry)
    assert "DB_URL" in result
    assert "3" in result


def test_empty_envs_returns_empty_report(calculator):
    report = calculator.calculate({})
    assert report.entries == []
    assert report.total_envs == 0


def test_formatter_format_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    formatter = FrequencyFormatter(color=False)
    output = formatter.format_report(report)
    assert "DB_URL" in output
    assert "Frequency" in output


def test_formatter_summary(calculator, three_envs):
    report = calculator.calculate(three_envs)
    formatter = FrequencyFormatter(color=False)
    summary = formatter.format_summary(report)
    assert "total keys" in summary
    assert "universal" in summary
