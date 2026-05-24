import pytest
from envdiff.key_provenance import ProvenanceCalculator
from envdiff.provenance_formatter import ProvenanceFormatter


@pytest.fixture
def calculator():
    return ProvenanceCalculator()


@pytest.fixture
def formatter():
    return ProvenanceFormatter(color=False)


@pytest.fixture
def sample_report(calculator):
    envs = {
        "dev": {"DB_URL": "postgres://localhost/dev", "APP_NAME": "myapp"},
        "prod": {"DB_URL": "postgres://prod/prod", "APP_NAME": "myapp"},
    }
    return calculator.calculate(envs)


def test_format_report_includes_header(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "Provenance" in output


def test_format_report_includes_env_names(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "dev" in output
    assert "prod" in output


def test_format_report_includes_all_keys(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "DB_URL" in output
    assert "APP_NAME" in output


def test_format_report_marks_inconsistent(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "inconsistent" in output


def test_format_report_marks_consistent(formatter, sample_report):
    output = formatter.format_report(sample_report)
    assert "consistent" in output


def test_format_summary_no_issues(formatter, calculator):
    envs = {"a": {"K": "v"}, "b": {"K": "v"}}
    report = calculator.calculate(envs)
    summary = formatter.format_summary(report)
    assert "consistent" in summary.lower()


def test_format_summary_with_issues(formatter, sample_report):
    summary = formatter.format_summary(sample_report)
    assert "inconsistent" in summary.lower()


def test_format_empty_report(formatter, calculator):
    report = calculator.calculate({})
    output = formatter.format_report(report)
    assert "No keys" in output
