import pytest
from envdiff.key_accessibility import AccessibilityChecker, AccessibilityReport


@pytest.fixture
def checker():
    return AccessibilityChecker(required_keys={"DATABASE_URL", "SECRET_KEY", "DEBUG"})


@pytest.fixture
def three_envs():
    return {
        "production": {
            "DATABASE_URL": "postgres://prod/db",
            "SECRET_KEY": "supersecret",
            "DEBUG": "false",
        },
        "staging": {
            "DATABASE_URL": "postgres://staging/db",
            "SECRET_KEY": "",
            "DEBUG": "true",
        },
        "development": {
            "DATABASE_URL": "postgres://localhost/db",
            "DEBUG": "true",
        },
    }


def test_calculate_returns_report(checker, three_envs):
    report = checker.calculate(three_envs)
    assert isinstance(report, AccessibilityReport)


def test_env_names_captured(checker, three_envs):
    report = checker.calculate(three_envs)
    assert set(report.env_names) == {"production", "staging", "development"}


def test_clean_env_has_no_issues(checker):
    envs = {
        "production": {
            "DATABASE_URL": "postgres://prod/db",
            "SECRET_KEY": "s3cr3t",
            "DEBUG": "false",
        }
    }
    report = checker.calculate(envs)
    assert not report.has_issues
    assert report.issues_for_env("production") == []


def test_missing_key_flagged(checker, three_envs):
    report = checker.calculate(three_envs)
    dev_issues = report.issues_for_env("development")
    keys = {i.key for i in dev_issues}
    assert "SECRET_KEY" in keys


def test_empty_key_flagged(checker, three_envs):
    report = checker.calculate(three_envs)
    staging_issues = report.issues_for_env("staging")
    keys = {i.key for i in staging_issues}
    assert "SECRET_KEY" in keys
    reasons = {i.reason for i in staging_issues if i.key == "SECRET_KEY"}
    assert any("empty" in r for r in reasons)


def test_has_issues_true_when_problems_exist(checker, three_envs):
    report = checker.calculate(three_envs)
    assert report.has_issues


def test_affected_keys_returns_set(checker, three_envs):
    report = checker.calculate(three_envs)
    affected = report.affected_keys()
    assert isinstance(affected, set)
    assert "SECRET_KEY" in affected


def test_issue_str_includes_env_and_key(checker, three_envs):
    report = checker.calculate(three_envs)
    issue_strs = [str(i) for i in report.issues]
    assert any("development" in s and "SECRET_KEY" in s for s in issue_strs)


def test_custom_required_keys():
    checker = AccessibilityChecker(required_keys={"MY_CUSTOM_KEY"})
    envs = {"env_a": {"OTHER_KEY": "value"}}
    report = checker.calculate(envs)
    assert report.has_issues
    assert report.issues[0].key == "MY_CUSTOM_KEY"
