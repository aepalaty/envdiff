"""Tests for envdiff.lint — EnvLinter rules."""

import pytest
from envdiff.lint import EnvLinter, LintResult, LintIssue


@pytest.fixture
def linter():
    return EnvLinter()


def test_clean_env_passes(linter):
    env = {"DATABASE_URL": "postgres://localhost/db", "PORT": "8080"}
    result = linter.lint(env)
    assert result.is_clean


def test_lowercase_key_triggers_warning(linter):
    env = {"database_url": "postgres://localhost/db"}
    result = linter.lint(env)
    assert not result.is_clean
    assert any("uppercase" in i.message for i in result.warnings)


def test_allow_lowercase_suppresses_warning():
    linter = EnvLinter(allow_lowercase=True)
    env = {"database_url": "postgres://localhost/db"}
    result = linter.lint(env)
    assert result.is_clean


def test_empty_sensitive_key_is_error(linter):
    env = {"DB_PASSWORD": ""}
    result = linter.lint(env)
    assert len(result.errors) == 1
    assert result.errors[0].key == "DB_PASSWORD"
    assert result.errors[0].severity == "error"


def test_empty_non_sensitive_key_no_error(linter):
    env = {"FEATURE_FLAG": ""}
    result = linter.lint(env)
    # may have other warnings but not an error for empty value
    assert len(result.errors) == 0


def test_whitespace_value_triggers_warning(linter):
    env = {"APP_NAME": "  myapp  "}
    result = linter.lint(env)
    assert any("whitespace" in i.message for i in result.warnings)


def test_placeholder_value_triggers_warning(linter):
    for placeholder in ["TODO", "CHANGEME", "REPLACE_ME", "<value>"]:
        env = {"SOME_KEY": placeholder}
        result = linter.lint(env)
        assert any("placeholder" in i.message for i in result.warnings), (
            f"Expected placeholder warning for value '{placeholder}'"
        )


def test_multiple_issues_collected(linter):
    env = {
        "db_token": "",       # lowercase key + empty sensitive
        "APP_HOST": "  localhost  ",  # whitespace
    }
    result = linter.lint(env)
    assert len(result.issues) >= 3


def test_str_clean_result(linter):
    env = {"PORT": "8080"}
    result = linter.lint(env)
    assert str(result) == "No lint issues found."


def test_str_dirty_result(linter):
    env = {"DB_SECRET": ""}
    result = linter.lint(env)
    output = str(result)
    assert "[ERROR]" in output
    assert "DB_SECRET" in output


def test_lint_issue_str():
    issue = LintIssue("MY_KEY", "Something is wrong.", "warning")
    assert str(issue) == "[WARNING] MY_KEY: Something is wrong."
