"""Tests for envdiff.key_health module."""
import pytest

from envdiff.key_health import HealthScore, HealthReport, KeyHealthCalculator
from envdiff.key_entropy import EntropyReport, EntropyEntry
from envdiff.key_frequency import FrequencyReport, FrequencyEntry
from envdiff.lint import LintResult, LintIssue


@pytest.fixture
def all_keys():
    return ["DB_URL", "SECRET_KEY", "DEBUG", "PORT"]


@pytest.fixture
def entropy_report():
    return EntropyReport(
        entries=[
            EntropyEntry(key="DB_URL", value="postgres://host/db", entropy=3.2),
            EntropyEntry(key="SECRET_KEY", value="abc", entropy=1.1),
            EntropyEntry(key="DEBUG", value="true", entropy=1.9),
            EntropyEntry(key="PORT", value="5432", entropy=1.8),
        ]
    )


@pytest.fixture
def frequency_report():
    return FrequencyReport(
        total_envs=4,
        entries=[
            FrequencyEntry(key="DB_URL", count=4),
            FrequencyEntry(key="SECRET_KEY", count=4),
            FrequencyEntry(key="DEBUG", count=2),
            FrequencyEntry(key="PORT", count=3),
        ],
    )


@pytest.fixture
def lint_result():
    result = LintResult()
    result.issues.append(LintIssue(key="DEBUG", message="lowercase key", severity="warning"))
    return result


@pytest.fixture
def calculator(entropy_report, frequency_report, lint_result):
    return KeyHealthCalculator(
        entropy_report=entropy_report,
        frequency_report=frequency_report,
        lint_result=lint_result,
    )


def test_calculate_returns_report(calculator, all_keys):
    report = calculator.calculate(all_keys)
    assert isinstance(report, HealthReport)
    assert len(report.scores) == 4


def test_all_keys_present_in_report(calculator, all_keys):
    report = calculator.calculate(all_keys)
    keys_in_report = {s.key for s in report.scores}
    assert keys_in_report == set(all_keys)


def test_scores_are_between_zero_and_one(calculator, all_keys):
    report = calculator.calculate(all_keys)
    for score in report.scores:
        assert 0.0 <= score.score <= 1.0


def test_lint_flagged_key_has_lower_score(calculator, all_keys):
    report = calculator.calculate(all_keys)
    debug_score = next(s for s in report.scores if s.key == "DEBUG")
    db_score = next(s for s in report.scores if s.key == "DB_URL")
    assert debug_score.score < db_score.score


def test_lint_flagged_key_has_reason(calculator, all_keys):
    report = calculator.calculate(all_keys)
    debug_score = next(s for s in report.scores if s.key == "DEBUG")
    assert any("lint" in r for r in debug_score.reasons)


def test_low_entropy_key_has_reason(calculator, all_keys):
    report = calculator.calculate(all_keys)
    secret_score = next(s for s in report.scores if s.key == "SECRET_KEY")
    assert any("entropy" in r for r in secret_score.reasons)


def test_average_score_is_float(calculator, all_keys):
    report = calculator.calculate(all_keys)
    avg = report.average_score()
    assert isinstance(avg, float)
    assert 0.0 <= avg <= 1.0


def test_poor_keys_below_threshold(calculator, all_keys):
    report = calculator.calculate(all_keys)
    poor = report.poor_keys(threshold=0.5)
    for s in poor:
        assert s.score < 0.5


def test_health_score_grade_a(all_keys):
    s = HealthScore(key="X", score=0.9)
    assert s.grade() == "A"


def test_health_score_grade_f(all_keys):
    s = HealthScore(key="X", score=0.1)
    assert s.grade() == "F"


def test_no_inputs_produces_midpoint_scores(all_keys):
    calc = KeyHealthCalculator()
    report = calc.calculate(all_keys)
    assert len(report.scores) == len(all_keys)
    for s in report.scores:
        assert s.score > 0.0


def test_top_keys_returns_highest_scores(calculator, all_keys):
    report = calculator.calculate(all_keys)
    top = report.top_keys(n=2)
    assert len(top) == 2
    assert top[0].score >= top[1].score
