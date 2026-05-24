import pytest
from envdiff.key_benchmarks import BenchmarkCalculator, BenchmarkReport, _is_sensitive, _score_entry
from envdiff.benchmark_formatter import BenchmarkFormatter


@pytest.fixture
def calculator():
    return BenchmarkCalculator()


@pytest.fixture
def three_envs():
    return {
        "production": {
            "DB_URL": "postgres://host/db",
            "DB_PASSWORD": "s3cr3tpassword!!",
            "APP_NAME": "myapp",
        },
        "staging": {
            "DB_URL": "postgres://staging/db",
            "DB_PASSWORD": "weak",
            "APP_NAME": "myapp",
        },
        "development": {
            "DB_URL": "postgres://localhost/db",
            "DB_PASSWORD": "",
            "APP_NAME": "myapp",
        },
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, BenchmarkReport)


def test_env_names_captured(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.env_names) == {"production", "staging", "development"}


def test_all_entries_created(calculator, three_envs):
    report = calculator.calculate(three_envs)
    # 3 envs x 3 keys = 9 entries
    assert len(report.entries) == 9


def test_is_sensitive_detects_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_detects_token():
    assert _is_sensitive("API_TOKEN") is True


def test_is_sensitive_ignores_plain_key():
    assert _is_sensitive("APP_NAME") is False


def test_score_empty_value_is_zero():
    assert _score_entry("DB_PASSWORD", "") == 0.0


def test_score_sensitive_short_value_penalized():
    score = _score_entry("DB_PASSWORD", "weak")
    assert score < 0.6


def test_score_non_sensitive_normal_value():
    score = _score_entry("APP_NAME", "myapp")
    assert score >= 0.7


def test_poor_keys_identifies_weak_entries(calculator, three_envs):
    report = calculator.calculate(three_envs)
    poor = report.poor_keys()
    poor_key_names = {e.key for e in poor}
    assert "DB_PASSWORD" in poor_key_names


def test_good_keys_identifies_strong_entries(calculator, three_envs):
    report = calculator.calculate(three_envs)
    good = report.good_keys()
    good_key_names = {e.key for e in good}
    assert "APP_NAME" in good_key_names


def test_entries_for_env_filters_correctly(calculator, three_envs):
    report = calculator.calculate(three_envs)
    prod_entries = report.entries_for_env("production")
    assert len(prod_entries) == 3
    assert all(e.env_name == "production" for e in prod_entries)


def test_average_score_is_float(calculator, three_envs):
    report = calculator.calculate(three_envs)
    avg = report.average_score()
    assert isinstance(avg, float)
    assert 0.0 <= avg <= 1.0


def test_formatter_includes_env_name(calculator, three_envs):
    report = calculator.calculate(three_envs)
    formatter = BenchmarkFormatter(use_color=False)
    output = formatter.format_report(report)
    assert "production" in output
    assert "staging" in output


def test_formatter_includes_key_names(calculator, three_envs):
    report = calculator.calculate(three_envs)
    formatter = BenchmarkFormatter(use_color=False)
    output = formatter.format_report(report)
    assert "DB_PASSWORD" in output
    assert "APP_NAME" in output
