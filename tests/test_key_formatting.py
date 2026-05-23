import pytest
from envdiff.key_formatting import FormattingChecker, FormattingReport
from envdiff.formatting_formatter import FormattingFormatter


@pytest.fixture
def checker():
    return FormattingChecker()


@pytest.fixture
def three_envs():
    return {
        "dev": {
            "APP_NAME": "myapp",
            "DB_URL": "postgres://localhost/dev",
            "SECRET_KEY": "devsecret",
        },
        "staging": {
            "APP_NAME": " myapp ",
            "DB_URL": "'postgres://localhost/staging",
            "SECRET_KEY": "stagingsecret",
        },
        "prod": {
            "APP_NAME": '"myapp"',
            "DB_URL": "postgres://localhost/prod",
            "SECRET_KEY": "prodsecret",
        },
    }


def test_calculate_returns_report(checker, three_envs):
    report = checker.calculate(three_envs)
    assert isinstance(report, FormattingReport)


def test_env_names_captured(checker, three_envs):
    report = checker.calculate(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_clean_env_has_no_issues(checker):
    envs = {"dev": {"APP_NAME": "myapp", "PORT": "8080"}}
    report = checker.calculate(envs)
    assert not report.has_issues()


def test_detects_trailing_whitespace(checker, three_envs):
    report = checker.calculate(three_envs)
    issue_types = [i.issue_type for i in report.issues]
    assert "trailing_whitespace" in issue_types


def test_trailing_whitespace_identifies_correct_key(checker):
    envs = {"dev": {"APP_NAME": " myapp ", "PORT": "8080"}}
    report = checker.calculate(envs)
    affected = [i.key for i in report.issues if i.issue_type == "trailing_whitespace"]
    assert "APP_NAME" in affected
    assert "PORT" not in affected


def test_detects_inconsistent_quotes(checker, three_envs):
    report = checker.calculate(three_envs)
    issue_types = [i.issue_type for i in report.issues]
    assert "inconsistent_quotes" in issue_types


def test_detects_unnecessary_quotes(checker):
    envs = {"dev": {"APP_NAME": '"myapp"'}}
    report = checker.calculate(envs)
    issue_types = [i.issue_type for i in report.issues]
    assert "unnecessary_quotes" in issue_types


def test_sensitive_key_skips_unnecessary_quotes(checker):
    envs = {"dev": {"SECRET_KEY": '"mysecret"'}}
    report = checker.calculate(envs)
    issue_types = [i.issue_type for i in report.issues]
    assert "unnecessary_quotes" not in issue_types


def test_issues_for_env_filters_correctly(checker, three_envs):
    report = checker.calculate(three_envs)
    staging_issues = report.issues_for_env("staging")
    assert all(i.env_name == "staging" for i in staging_issues)


def test_issues_for_key_filters_correctly(checker, three_envs):
    report = checker.calculate(three_envs)
    app_issues = report.issues_for_key("APP_NAME")
    assert all(i.key == "APP_NAME" for i in app_issues)


def test_formatter_clean_report(checker):
    formatter = FormattingFormatter(use_color=False)
    envs = {"dev": {"APP_NAME": "myapp"}}
    report = checker.calculate(envs)
    output = formatter.format_report(report)
    assert "No formatting issues" in output


def test_formatter_dirty_report(checker, three_envs):
    formatter = FormattingFormatter(use_color=False)
    report = checker.calculate(three_envs)
    output = formatter.format_report(report)
    assert "formatting issue" in output.lower()


def test_format_summary_ok(checker):
    formatter = FormattingFormatter(use_color=False)
    envs = {"dev": {"APP_NAME": "myapp"}}
    report = checker.calculate(envs)
    assert "OK" in formatter.format_summary(report)


def test_format_summary_issues(checker, three_envs):
    formatter = FormattingFormatter(use_color=False)
    report = checker.calculate(three_envs)
    assert "issue" in formatter.format_summary(report)
