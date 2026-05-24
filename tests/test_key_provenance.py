import pytest
from envdiff.key_provenance import ProvenanceCalculator, ProvenanceReport


@pytest.fixture
def calculator():
    return ProvenanceCalculator()


@pytest.fixture
def three_envs():
    return {
        "dev": {
            "DB_URL": "postgres://localhost/dev",
            "APP_NAME": "myapp",
            "DEBUG": "true",
        },
        "staging": {
            "DB_URL": "postgres://staging-host/staging",
            "APP_NAME": "myapp",
            "SECRET_KEY": "abc123",
        },
        "prod": {
            "DB_URL": "postgres://prod-host/prod",
            "APP_NAME": "myapp",
            "SECRET_KEY": "xyz789",
        },
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, ProvenanceReport)


def test_env_names_captured(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_all_keys_collected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    keys = {e.key for e in report.entries}
    assert keys == {"DB_URL", "APP_NAME", "DEBUG", "SECRET_KEY"}


def test_db_url_in_all_sources(calculator, three_envs):
    report = calculator.calculate(three_envs)
    db_entry = next(e for e in report.entries if e.key == "DB_URL")
    assert set(db_entry.sources) == {"dev", "staging", "prod"}


def test_db_url_is_inconsistent(calculator, three_envs):
    report = calculator.calculate(three_envs)
    db_entry = next(e for e in report.entries if e.key == "DB_URL")
    assert db_entry.value_consistent is False


def test_app_name_is_consistent(calculator, three_envs):
    report = calculator.calculate(three_envs)
    app_entry = next(e for e in report.entries if e.key == "APP_NAME")
    assert app_entry.value_consistent is True


def test_debug_single_source(calculator, three_envs):
    report = calculator.calculate(three_envs)
    debug_entry = next(e for e in report.entries if e.key == "DEBUG")
    assert debug_entry.sources == ["dev"]
    assert debug_entry.first_source == "dev"


def test_keys_from_single_source(calculator, three_envs):
    report = calculator.calculate(three_envs)
    single = report.keys_from_single_source()
    assert "DEBUG" in single
    assert "APP_NAME" not in single


def test_inconsistent_keys(calculator, three_envs):
    report = calculator.calculate(three_envs)
    inconsistent = report.inconsistent_keys()
    assert "DB_URL" in inconsistent
    assert "APP_NAME" not in inconsistent


def test_has_inconsistencies_true(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert report.has_inconsistencies() is True


def test_has_inconsistencies_false(calculator):
    envs = {
        "a": {"KEY": "value"},
        "b": {"KEY": "value"},
    }
    report = calculator.calculate(envs)
    assert report.has_inconsistencies() is False


def test_empty_envs(calculator):
    report = calculator.calculate({})
    assert report.entries == []
    assert report.has_inconsistencies() is False
