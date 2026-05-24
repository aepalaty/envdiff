import pytest
from envdiff.key_dependencies import DependencyChecker, DependencyReport, DependencyViolation


@pytest.fixture
def checker():
    return DependencyChecker(
        rules={
            "DB_HOST": ["DB_PORT", "DB_NAME"],
            "REDIS_URL": ["REDIS_PASSWORD"],
        }
    )


@pytest.fixture
def three_envs():
    return {
        "prod": {
            "DB_HOST": "db.prod.example.com",
            "DB_PORT": "5432",
            "DB_NAME": "mydb",
            "REDIS_URL": "redis://localhost",
            "REDIS_PASSWORD": "secret",
        },
        "staging": {
            "DB_HOST": "db.staging.example.com",
            "DB_PORT": "5432",
            # DB_NAME missing
            "REDIS_URL": "redis://localhost",
            "REDIS_PASSWORD": "stagingsecret",
        },
        "dev": {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "devdb",
            # REDIS_URL present but REDIS_PASSWORD missing
            "REDIS_URL": "redis://localhost",
        },
    }


def test_calculate_returns_report(checker, three_envs):
    report = checker.calculate(three_envs)
    assert isinstance(report, DependencyReport)


def test_env_names_captured(checker, three_envs):
    report = checker.calculate(three_envs)
    assert set(report.env_names) == {"prod", "staging", "dev"}


def test_clean_env_has_no_violations(checker, three_envs):
    report = checker.calculate({"prod": three_envs["prod"]})
    assert not report.has_violations


def test_missing_dependency_detected(checker, three_envs):
    report = checker.calculate(three_envs)
    keys_with_violations = report.violation_keys()
    assert "DB_HOST" in keys_with_violations


def test_staging_missing_db_name(checker, three_envs):
    report = checker.calculate(three_envs)
    staging_violations = report.violations_for_env("staging")
    missing_reqs = {v.requires for v in staging_violations}
    assert "DB_NAME" in missing_reqs


def test_dev_missing_redis_password(checker, three_envs):
    report = checker.calculate(three_envs)
    dev_violations = report.violations_for_env("dev")
    missing_reqs = {v.requires for v in dev_violations}
    assert "REDIS_PASSWORD" in missing_reqs


def test_no_violation_when_key_absent(checker):
    # If the key itself is absent, no dependency check is triggered
    env = {"SOME_OTHER_KEY": "value"}
    report = checker.calculate({"test": env})
    assert not report.has_violations


def test_violation_str_format(checker, three_envs):
    report = checker.calculate(three_envs)
    v = report.violations[0]
    s = str(v)
    assert v.env_name in s
    assert v.key in s
    assert v.requires in s
