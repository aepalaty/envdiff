"""Tests for key_complexity module."""
import pytest
from envdiff.key_complexity import ComplexityCalculator, ComplexityReport


@pytest.fixture
def calculator() -> ComplexityCalculator:
    return ComplexityCalculator()


@pytest.fixture
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "AWS_S3_BUCKET_NAME": "my-bucket",
        "PORT": "8080",
        "APP_FEATURE_FLAG_NEW_UI_ENABLED": "true",
    }


def test_calculate_returns_report(calculator, sample_env):
    report = calculator.calculate("prod", sample_env)
    assert isinstance(report, ComplexityReport)
    assert report.env_name == "prod"
    assert len(report.entries) == len(sample_env)


def test_all_keys_present(calculator, sample_env):
    report = calculator.calculate("prod", sample_env)
    keys = {e.key for e in report.entries}
    assert keys == set(sample_env.keys())


def test_depth_single_segment(calculator):
    report = calculator.calculate("test", {"PORT": "8080"})
    entry = report.entries[0]
    assert entry.depth == 1


def test_depth_multi_segment(calculator):
    report = calculator.calculate("test", {"AWS_S3_BUCKET_NAME": "x"})
    entry = report.entries[0]
    assert entry.depth == 4


def test_namespaced_key_detected(calculator):
    report = calculator.calculate("test", {"DB_HOST": "localhost"})
    entry = report.entries[0]
    assert entry.is_namespaced is True


def test_non_namespaced_key(calculator):
    report = calculator.calculate("test", {"PORT": "8080"})
    entry = report.entries[0]
    assert entry.is_namespaced is False


def test_score_is_between_zero_and_one(calculator, sample_env):
    report = calculator.calculate("prod", sample_env)
    for entry in report.entries:
        assert 0.0 <= entry.score <= 1.0


def test_deeply_nested_threshold(calculator):
    env = {
        "A_B": "1",           # depth 2 — not deeply nested
        "A_B_C": "2",         # depth 3 — deeply nested
        "A_B_C_D": "3",       # depth 4 — deeply nested
    }
    report = calculator.calculate("test", env)
    nested_keys = {e.key for e in report.deeply_nested}
    assert "A_B_C" in nested_keys
    assert "A_B_C_D" in nested_keys
    assert "A_B" not in nested_keys


def test_most_complex_sorted_descending(calculator, sample_env):
    report = calculator.calculate("prod", sample_env)
    scores = [e.score for e in report.most_complex]
    assert scores == sorted(scores, reverse=True)


def test_average_score_empty_env(calculator):
    report = calculator.calculate("empty", {})
    assert report.average_score == 0.0


def test_calculate_all_returns_dict(calculator, sample_env):
    envs = {"prod": sample_env, "dev": {"PORT": "3000"}}
    reports = calculator.calculate_all(envs)
    assert set(reports.keys()) == {"prod", "dev"}
    assert all(isinstance(r, ComplexityReport) for r in reports.values())


def test_longer_key_has_higher_length_score(calculator):
    short = calculator.calculate("t", {"A": "1"}).entries[0]
    long_ = calculator.calculate("t", {"AVERYLONGKEYNAME_WITH_MANY_CHARS_EXTRA": "1"}).entries[0]
    assert long_.length > short.length
