"""Tests for key correlation detection."""
import pytest
from envdiff.key_correlation import KeyCorrelationCalculator, CorrelationReport
from envdiff.correlation_formatter import CorrelationFormatter


@pytest.fixture
def calculator():
    return KeyCorrelationCalculator()


@pytest.fixture
def three_envs():
    return {
        "dev": {"DB_URL": "dev_db", "DB_PASS": "dev_pass", "PORT": "3000"},
        "staging": {"DB_URL": "stg_db", "DB_PASS": "stg_pass", "PORT": "8080"},
        "prod": {"DB_URL": "prod_db", "DB_PASS": "prod_pass", "SECRET": "xyz"},
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, CorrelationReport)


def test_env_names_captured(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_db_url_and_db_pass_always_together(calculator, three_envs):
    report = calculator.calculate(three_envs, min_score=0.0)
    pair = next(
        (e for e in report.entries if {e.key_a, e.key_b} == {"DB_URL", "DB_PASS"}),
        None,
    )
    assert pair is not None
    assert pair.score == 1.0


def test_strong_pairs_returns_only_perfect_score(calculator, three_envs):
    report = calculator.calculate(three_envs, min_score=0.0)
    for entry in report.strong_pairs:
        assert entry.score == 1.0


def test_partial_pairs_excludes_perfect_score(calculator, three_envs):
    report = calculator.calculate(three_envs, min_score=0.0)
    for entry in report.partial_pairs:
        assert 0.0 < entry.score < 1.0


def test_min_score_filters_entries(calculator, three_envs):
    report_all = calculator.calculate(three_envs, min_score=0.0)
    report_strict = calculator.calculate(three_envs, min_score=1.0)
    assert len(report_strict.entries) <= len(report_all.entries)
    for e in report_strict.entries:
        assert e.score == 1.0


def test_empty_envs_returns_empty_report(calculator):
    report = calculator.calculate({})
    assert report.entries == []
    assert report.env_names == []


def test_single_env_no_co_occurrence(calculator):
    report = calculator.calculate({"dev": {"A": "1", "B": "2"}}, min_score=0.0)
    # With a single env, both keys co-occur in 1/1 envs
    pair = next(
        (e for e in report.entries if {e.key_a, e.key_b} == {"A", "B"}),
        None,
    )
    assert pair is not None
    assert pair.score == 1.0


def test_top_limits_results(calculator, three_envs):
    report = calculator.calculate(three_envs, min_score=0.0)
    assert len(report.top(2)) <= 2


def test_formatter_produces_string(three_envs):
    calculator = KeyCorrelationCalculator()
    report = calculator.calculate(three_envs, min_score=0.0)
    formatter = CorrelationFormatter(color=False)
    output = formatter.format_report(report)
    assert "Correlation" in output
    assert "DB_URL" in output


def test_formatter_no_entries_message(three_envs):
    calculator = KeyCorrelationCalculator()
    report = calculator.calculate(three_envs, min_score=1.1)  # impossible threshold
    formatter = CorrelationFormatter(color=False)
    output = formatter.format_report(report)
    assert "No correlated" in output
