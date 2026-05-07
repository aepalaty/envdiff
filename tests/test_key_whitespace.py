import pytest
from envdiff.key_whitespace import WhitespaceChecker, WhitespaceReport, WhitespaceIssue


@pytest.fixture
def checker():
    return WhitespaceChecker()


@pytest.fixture
def three_envs():
    return {
        "dev": {
            "DB_HOST": "localhost",
            "DB_PASS": " secret",
            "APP_NAME": "myapp  ",
        },
        "staging": {
            "DB_HOST": "db.staging.local",
            "DB_PASS": "secret",
            "APP_NAME": "myapp",
        },
        "prod": {
            "DB_HOST": "db.prod.local",
            "DB_PASS": "secret",
            "APP_NAME": "myapp",
        },
    }


def test_calculate_returns_report(checker, three_envs):
    report = checker.calculate(three_envs)
    assert isinstance(report, WhitespaceReport)


def test_env_names_captured(checker, three_envs):
    report = checker.calculate(three_envs)
    assert "dev" in report.env_names
    assert "staging" in report.env_names


def test_clean_env_has_no_issues(checker):
    envs = {"clean": {"KEY": "value", "OTHER": "hello"}}
    report = checker.calculate(envs)
    assert not report.has_issues()


def test_detects_leading_whitespace(checker):
    envs = {"dev": {"DB_PASS": " secret"}}
    report = checker.calculate(envs)
    assert report.has_issues()
    issue = report.issues[0]
    assert issue.leading is True
    assert issue.trailing is False


def test_detects_trailing_whitespace(checker):
    envs = {"dev": {"APP_NAME": "myapp  "}}
    report = checker.calculate(envs)
    assert report.has_issues()
    issue = report.issues[0]
    assert issue.trailing is True
    assert issue.leading is False


def test_detects_internal_whitespace(checker):
    envs = {"dev": {"GREETING": "hello  world"}}
    report = checker.calculate(envs)
    assert report.has_issues()
    issue = report.issues[0]
    assert issue.internal is True


def test_detects_internal_tab(checker):
    envs = {"dev": {"GREETING": "hello\tworld"}}
    report = checker.calculate(envs)
    assert report.has_issues()
    assert report.issues[0].internal is True


def test_issues_for_env_filters_correctly(checker, three_envs):
    report = checker.calculate(three_envs)
    dev_issues = report.issues_for_env("dev")
    assert all(i.env_name == "dev" for i in dev_issues)


def test_affected_keys_returns_unique_sorted(checker):
    envs = {
        "dev": {"A": " val", "B": "ok"},
        "staging": {"A": "val ", "B": "ok"},
    }
    report = checker.calculate(envs)
    assert report.affected_keys() == ["A"]


def test_str_representation(checker):
    envs = {"dev": {"DB_PASS": " secret "}}
    report = checker.calculate(envs)
    s = str(report.issues[0])
    assert "DB_PASS" in s
    assert "dev" in s
