"""Tests for key inheritance detection."""
import pytest
from envdiff.key_inheritance import InheritanceDetector, InheritanceEntry, InheritanceReport
from envdiff.inheritance_formatter import InheritanceFormatter


@pytest.fixture
def detector():
    return InheritanceDetector()


@pytest.fixture
def base_env():
    return {
        "DB_URL": "postgres://localhost/base",
        "SECRET_KEY": "base-secret",
        "DEBUG": "false",
    }


@pytest.fixture
def other_envs():
    return {
        "staging": {
            "DB_URL": "postgres://staging/app",
            "SECRET_KEY": "base-secret",
            "DEBUG": "false",
        },
        "production": {
            "DB_URL": "postgres://prod/app",
            "SECRET_KEY": "prod-secret",
            "DEBUG": "false",
        },
    }


def test_calculate_returns_report(detector, base_env, other_envs):
    report = detector.calculate(base_env, other_envs, base_name="base")
    assert isinstance(report, InheritanceReport)
    assert report.base_name == "base"


def test_all_keys_collected(detector, base_env, other_envs):
    report = detector.calculate(base_env, other_envs)
    keys = [e.key for e in report.entries]
    assert "DB_URL" in keys
    assert "SECRET_KEY" in keys
    assert "DEBUG" in keys


def test_overridden_key_detected(detector, base_env, other_envs):
    report = detector.calculate(base_env, other_envs)
    db_entry = next(e for e in report.entries if e.key == "DB_URL")
    assert db_entry.is_overridden
    assert "staging" in db_entry.override_envs
    assert "production" in db_entry.override_envs


def test_inherited_key_not_flagged(detector, base_env, other_envs):
    report = detector.calculate(base_env, other_envs)
    debug_entry = next(e for e in report.entries if e.key == "DEBUG")
    assert not debug_entry.is_overridden
    assert debug_entry.override_envs == []


def test_partially_overridden_key(detector, base_env, other_envs):
    report = detector.calculate(base_env, other_envs)
    secret_entry = next(e for e in report.entries if e.key == "SECRET_KEY")
    assert secret_entry.is_overridden
    assert "production" in secret_entry.override_envs
    assert "staging" not in secret_entry.override_envs


def test_overridden_keys_list(detector, base_env, other_envs):
    report = detector.calculate(base_env, other_envs)
    assert "DB_URL" in report.overridden_keys
    assert "SECRET_KEY" in report.overridden_keys
    assert "DEBUG" not in report.overridden_keys


def test_inherited_keys_list(detector, base_env, other_envs):
    report = detector.calculate(base_env, other_envs)
    assert "DEBUG" in report.inherited_keys


def test_has_overrides_true(detector, base_env, other_envs):
    report = detector.calculate(base_env, other_envs)
    assert report.has_overrides is True


def test_has_overrides_false_when_all_match(detector):
    base = {"KEY": "val"}
    others = {"env1": {"KEY": "val"}, "env2": {"KEY": "val"}}
    report = detector.calculate(base, others)
    assert report.has_overrides is False


def test_entry_str_inherited(detector):
    entry = InheritanceEntry(key="DEBUG", base_value="false", overrides={"staging": "false"})
    assert "inherited" in str(entry)


def test_entry_str_overridden(detector):
    entry = InheritanceEntry(key="DB_URL", base_value="old", overrides={"prod": "new"})
    assert "overridden" in str(entry)
    assert "prod" in str(entry)


def test_formatter_output(detector, base_env, other_envs):
    report = detector.calculate(base_env, other_envs, base_name="base")
    formatter = InheritanceFormatter(color=False)
    output = formatter.format_report(report)
    assert "Inheritance Report" in output
    assert "DB_URL" in output
    assert "inherited" in output or "overridden" in output


def test_formatter_summary_counts(detector, base_env, other_envs):
    report = detector.calculate(base_env, other_envs)
    formatter = InheritanceFormatter(color=False)
    output = formatter.format_report(report)
    assert "inherited" in output
    assert "overridden" in output


def test_extra_key_in_child_env(detector):
    base = {"SHARED": "val"}
    others = {"staging": {"SHARED": "val", "EXTRA_KEY": "only-in-staging"}}
    report = detector.calculate(base, others)
    keys = [e.key for e in report.entries]
    assert "EXTRA_KEY" in keys
