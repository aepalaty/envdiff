import pytest
from envdiff.key_symmetry import SymmetryCalculator, SymmetryReport, SymmetryEntry


@pytest.fixture
def calculator():
    return SymmetryCalculator()


@pytest.fixture
def three_envs():
    return {
        "dev": {"DB_URL": "dev-db", "APP_NAME": "myapp", "DEBUG": "true"},
        "staging": {"DB_URL": "staging-db", "APP_NAME": "myapp"},
        "prod": {"DB_URL": "prod-db", "APP_NAME": "myapp", "SECRET_KEY": "abc123"},
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, SymmetryReport)


def test_env_names_captured(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_all_keys_collected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    keys = {e.key for e in report.entries}
    assert keys == {"DB_URL", "APP_NAME", "DEBUG", "SECRET_KEY"}


def test_symmetric_key_has_no_absent_envs(calculator, three_envs):
    report = calculator.calculate(three_envs)
    app_name = next(e for e in report.entries if e.key == "APP_NAME")
    assert app_name.is_symmetric()
    assert app_name.absent_from == []


def test_asymmetric_key_reports_missing_envs(calculator, three_envs):
    report = calculator.calculate(three_envs)
    debug = next(e for e in report.entries if e.key == "DEBUG")
    assert not debug.is_symmetric()
    assert "staging" in debug.absent_from
    assert "prod" in debug.absent_from


def test_has_asymmetry_true_when_keys_missing(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert report.has_asymmetry()


def test_has_asymmetry_false_when_all_match(calculator):
    envs = {
        "dev": {"KEY": "a"},
        "prod": {"KEY": "b"},
    }
    report = calculator.calculate(envs)
    assert not report.has_asymmetry()


def test_symmetry_ratio_all_symmetric(calculator):
    envs = {
        "dev": {"A": "1", "B": "2"},
        "prod": {"A": "1", "B": "2"},
    }
    report = calculator.calculate(envs)
    assert report.symmetry_ratio() == 1.0


def test_symmetry_ratio_partial(calculator, three_envs):
    report = calculator.calculate(three_envs)
    ratio = report.symmetry_ratio()
    assert 0.0 < ratio < 1.0


def test_str_symmetric_entry():
    entry = SymmetryEntry(key="DB_URL", present_in=["dev", "prod"], absent_from=[])
    assert "present in all" in str(entry)


def test_str_asymmetric_entry():
    entry = SymmetryEntry(key="DEBUG", present_in=["dev"], absent_from=["prod", "staging"])
    result = str(entry)
    assert "DEBUG" in result
    assert "prod" in result
    assert "staging" in result
