import pytest
from envdiff.key_whitespace import WhitespaceChecker, WhitespaceReport
from envdiff.whitespace_formatter import WhitespaceFormatter


@pytest.fixture
def checker():
    return WhitespaceChecker()


@pytest.fixture
def formatter():
    return WhitespaceFormatter(color=False)


@pytest.fixture
def clean_report():
    return WhitespaceReport(env_names=["dev"], issues=[])


@pytest.fixture
def dirty_report(checker):
    envs = {
        "dev": {"DB_PASS": " secret", "APP_NAME": "myapp  "},
        "prod": {"DB_PASS": "secret", "APP_NAME": "myapp"},
    }
    return checker.calculate(envs)


def test_format_clean_report_says_no_issues(formatter, clean_report):
    output = formatter.format_report(clean_report)
    assert "No whitespace issues found" in output


def test_format_dirty_report_includes_key(formatter, dirty_report):
    output = formatter.format_report(dirty_report)
    assert "DB_PASS" in output


def test_format_dirty_report_includes_env_name(formatter, dirty_report):
    output = formatter.format_report(dirty_report)
    assert "dev" in output


def test_format_dirty_report_shows_total(formatter, dirty_report):
    output = formatter.format_report(dirty_report)
    assert "Total issues" in output


def test_format_summary_clean(formatter, clean_report):
    summary = formatter.format_summary(clean_report)
    assert "clean" in summary


def test_format_summary_dirty(formatter, dirty_report):
    summary = formatter.format_summary(dirty_report)
    assert "issue" in summary


def test_no_color_mode_omits_escape_codes(dirty_report):
    fmt = WhitespaceFormatter(color=False)
    output = fmt.format_report(dirty_report)
    assert "\033[" not in output


def test_color_mode_includes_escape_codes(dirty_report):
    fmt = WhitespaceFormatter(color=True)
    output = fmt.format_report(dirty_report)
    assert "\033[" in output
