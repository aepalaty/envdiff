import pytest
from envdiff.key_dependencies import DependencyChecker
from envdiff.dependency_formatter import DependencyFormatter


@pytest.fixture
def checker():
    return DependencyChecker(rules={"DB_HOST": ["DB_PORT"], "REDIS_URL": ["REDIS_PASSWORD"]})


@pytest.fixture
def formatter():
    return DependencyFormatter(color=False)


@pytest.fixture
def clean_report(checker):
    envs = {
        "prod": {"DB_HOST": "localhost", "DB_PORT": "5432"},
    }
    return checker.calculate(envs)


@pytest.fixture
def dirty_report(checker):
    envs = {
        "staging": {"DB_HOST": "localhost"},  # DB_PORT missing
        "dev": {"REDIS_URL": "redis://localhost"},  # REDIS_PASSWORD missing
    }
    return checker.calculate(envs)


def test_format_clean_report_says_no_issues(formatter, clean_report):
    output = formatter.format_report(clean_report)
    assert "No dependency violations found" in output


def test_format_dirty_report_includes_env_name(formatter, dirty_report):
    output = formatter.format_report(dirty_report)
    assert "staging" in output or "dev" in output


def test_format_dirty_report_includes_key_name(formatter, dirty_report):
    output = formatter.format_report(dirty_report)
    assert "DB_HOST" in output or "REDIS_URL" in output


def test_format_dirty_report_includes_required_key(formatter, dirty_report):
    output = formatter.format_report(dirty_report)
    assert "DB_PORT" in output or "REDIS_PASSWORD" in output


def test_format_dirty_report_includes_violation_count(formatter, dirty_report):
    output = formatter.format_report(dirty_report)
    assert "violation" in output


def test_format_summary_clean(formatter, clean_report):
    summary = formatter.format_summary(clean_report)
    assert "ok" in summary


def test_format_summary_dirty(formatter, dirty_report):
    summary = formatter.format_summary(dirty_report)
    assert "violation" in summary


def test_format_report_includes_header(formatter, dirty_report):
    output = formatter.format_report(dirty_report)
    assert "Dependency" in output
