import pytest
from envdiff.key_similarity import (
    KeySimilarityCalculator,
    SimilarityReport,
    SimilarityPair,
    _dice_coefficient,
)
from envdiff.similarity_formatter import SimilarityFormatter


@pytest.fixture
def calculator():
    return KeySimilarityCalculator(threshold=0.5)


@pytest.fixture
def three_envs():
    return {
        "prod": {
            "DB_HOST": "prod-db",
            "DB_PASS": "secret",
            "API_KEY": "abc",
            "API_SECRET": "xyz",
        },
        "staging": {
            "DB_HOST": "staging-db",
            "DB_PASSWORD": "hunter2",
            "API_KEY": "def",
        },
    }


def test_dice_identical_strings():
    assert _dice_coefficient("hello", "hello") == 1.0


def test_dice_completely_different():
    score = _dice_coefficient("abc", "xyz")
    assert score == 0.0


def test_dice_partial_overlap():
    score = _dice_coefficient("DB_PASS", "DB_PASSWORD")
    assert 0.0 < score < 1.0


def test_dice_short_strings_below_ngram():
    # strings shorter than n=2 yield 0.0
    assert _dice_coefficient("a", "b") == 0.0


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, SimilarityReport)


def test_db_pass_and_db_password_detected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    keys_in_pairs = {
        frozenset([p.key_a, p.key_b]) for p in report.pairs
    }
    assert frozenset(["DB_PASS", "DB_PASSWORD"]) in keys_in_pairs


def test_api_key_and_api_secret_detected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    keys_in_pairs = {
        frozenset([p.key_a, p.key_b]) for p in report.pairs
    }
    assert frozenset(["API_KEY", "API_SECRET"]) in keys_in_pairs


def test_scores_sorted_descending(calculator, three_envs):
    report = calculator.calculate(three_envs)
    scores = [p.score for p in report.pairs]
    assert scores == sorted(scores, reverse=True)


def test_above_correctly(calculator, three_envs):
    report = calculator.calculate(three_envs)
    high = report.above_threshold(0.9)
    assert all(p.score >= 0.9 for p in high)


def test_top_limits_results(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert len(report.top(2)) <= 2


def test_has_similar_false_when_no_pairs():
    report = SimilarityReport(pairs=[])
    assert not report.has_similar


def test_formatter_no_pairs_message():
    formatter = SimilarityFormatter(color=False)
    report = SimilarityReport(pairs=[])
    output = formatter.format_report(report)
    assert "No suspiciously similar" in output


def test_formatter_includes_key_names(three_envs):
    calculator = KeySimilarityCalculator(threshold=0.5)
    report = calculator.calculate(three_envs)
    formatter = SimilarityFormatter(color=False, threshold=0.5)
    output = formatter.format_report(report)
    assert "DB_PASS" in output
    assert "DB_PASSWORD" in output


def test_formatter_includes_total(three_envs):
    calculator = KeySimilarityCalculator(threshold=0.5)
    report = calculator.calculate(three_envs)
    formatter = SimilarityFormatter(color=False, threshold=0.5)
    output = formatter.format_report(report)
    assertn