"""Tests for envdiff.key_length."""
import pytest
from envdiff.key_length import KeyLengthChecker, LengthReport, LengthIssue


@pytest.fixture
def checker():
    return KeyLengthChecker(max_key_length=10, max_value_length=20)


@pytest.fixture
def three_envs():
    return {
        "prod": {
            "DB_URL": "postgres://localhost/db",
            "SHORT": "ok",
        },
        "staging": {
            "DB_URL": "postgres://staging/db",
            "A_VERY_LONG_KEY_NAME": "value",
        },
        "dev": {
            "DB_URL": "dev",
            "TOKEN": "x" * 25,
        },
    }


def test_calculate_returns_report(checker, three_envs):
    report = checker.check(three_envs)
    assert isinstance(report, LengthReport)


def test_env_names_captured(checker, three_envs):
    report = checker.check(three_envs)
    assert set(report.env_names) == {"prod", "staging", "dev"}


def test_clean_env_has_no_issues(checker):
    envs = {"prod": {"DB": "value", "PORT": "5432"}}
    report = checker.check(envs)
    assert not report.has_issues


def test_detects_long_key(checker, three_envs):
    report = checker.check(three_envs)
    key_issues = [i for i in report.issues if i.kind == "key"]
    assert any(i.key == "A_VERY_LONG_KEY_NAME" for i in key_issues)


def test_detects_long_value(checker, three_envs):
    report = checker.check(three_envs)
    value_issues = [i for i in report.issues if i.kind == "value"]
    assert any(i.key == "TOKEN" and i.env_name == "dev" for i in value_issues)


def test_long_key_issue_has_correct_length(checker, three_envs):
    report = checker.check(three_envs)
    issue = next(
        i for i in report.issues
        if i.key == "A_VERY_LONG_KEY_NAME" and i.kind == "key"
    )
    assert issue.length == len("A_VERY_LONG_KEY_NAME")
    assert issue.limit == 10


def test_long_value_issue_has_correct_length(checker, three_envs):
    report = checker.check(three_envs)
    issue = next(
        i for i in report.issues
        if i.key == "TOKEN" and i.kind == "value"
    )
    assert issue.length == 25
    assert issue.limit == 20


def test_issues_for_env_filters_correctly(checker, three_envs):
    report = checker.check(three_envs)
    dev_issues = report.issues_for_env("dev")
    assert all(i.env_name == "dev" for i in dev_issues)


def test_affected_keys_returns_unique_sorted(checker, three_envs):
    report = checker.check(three_envs)
    keys = report.affected_keys()
    assert keys == sorted(set(keys))
    assert "TOKEN" in keys
    assert "A_VERY_LONG_KEY_NAME" in keys


def test_str_representation_of_issue(checker):
    issue = LengthIssue(
        env_name="prod",
        key="MY_KEY",
        kind="value",
        length=600,
        limit=512,
    )
    text = str(issue)
    assert "prod" in text
    assert "MY_KEY" in text
    assert "600" in text
    assert "512" in text


def test_default_limits_are_permissive():
    checker = KeyLengthChecker()
    envs = {"prod": {"NORMAL_KEY": "normal_value"}}
    report = checker.check(envs)
    assert not report.has_issues
