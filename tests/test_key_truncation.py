import pytest
from envdiff.key_truncation import TruncationChecker, TruncationReport, TruncationIssue
from envdiff.truncation_formatter import TruncationFormatter


@pytest.fixture
def checker():
    return TruncationChecker(max_length=20)


@pytest.fixture
def three_envs():
    return {
        "dev": {
            "DB_URL": "postgres://localhost/dev",
            "SECRET": "short",
            "API_KEY": "abc123",
        },
        "staging": {
            "DB_URL": "postgres://staging.internal/myapp_staging_db",
            "SECRET": "a" * 50,
            "API_KEY": "xyz",
        },
        "prod": {
            "DB_URL": "postgres://prod.internal/myapp",
            "SECRET": "supersecretvalue",
            "API_KEY": "b" * 25,
        },
    }


def test_calculate_returns_report(checker, three_envs):
    report = checker.check(three_envs)
    assert isinstance(report, TruncationReport)


def test_env_names_captured(checker, three_envs):
    report = checker.check(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_clean_env_has_no_issues(checker):
    envs = {"dev": {"KEY": "short", "OTHER": "also_short"}}
    report = checker.check(envs)
    assert not report.has_issues()


def test_detects_long_value(checker, three_envs):
    report = checker.check(three_envs)
    keys_with_issues = report.affected_keys()
    assert "SECRET" in keys_with_issues or "DB_URL" in keys_with_issues or "API_KEY" in keys_with_issues


def test_issue_has_correct_fields(checker):
    envs = {"prod": {"TOKEN": "x" * 30}}
    report = checker.check(envs)
    assert report.has_issues()
    issue = report.issues[0]
    assert issue.env_name == "prod"
    assert issue.key == "TOKEN"
    assert issue.value_length == 30
    assert issue.max_length == 20


def test_issues_for_env_filters_correctly(checker, three_envs):
    report = checker.check(three_envs)
    staging_issues = report.issues_for_env("staging")
    assert all(i.env_name == "staging" for i in staging_issues)


def test_affected_keys_are_sorted(checker, three_envs):
    report = checker.check(three_envs)
    keys = report.affected_keys()
    assert keys == sorted(keys)


def test_issue_str_contains_key_and_env():
    issue = TruncationIssue(env_name="prod", key="TOKEN", value_length=300, max_length=256)
    s = str(issue)
    assert "TOKEN" in s
    assert "prod" in s
    assert "300" in s


def test_formatter_no_issues_message():
    formatter = TruncationFormatter(use_color=False)
    report = TruncationReport(env_names=["dev"], issues=[])
    output = formatter.format_report(report)
    assert "No truncation issues" in output


def test_formatter_shows_affected_key():
    formatter = TruncationFormatter(use_color=False)
    issue = TruncationIssue(env_name="dev", key="BIG_KEY", value_length=500, max_length=256)
    report = TruncationReport(env_names=["dev"], issues=[issue])
    output = formatter.format_report(report)
    assert "BIG_KEY" in output
    assert "500" in output
