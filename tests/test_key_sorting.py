import pytest
from envdiff.key_sorting import KeySortingChecker, SortingReport, SortedEnv


@pytest.fixture
def checker():
    return KeySortingChecker()


@pytest.fixture
def three_envs():
    return {
        "production": {
            "APP_NAME": "myapp",
            "DB_HOST": "prod-db",
            "DB_PORT": "5432",
            "SECRET_KEY": "abc123",
        },
        "staging": {
            "SECRET_KEY": "stg123",
            "APP_NAME": "myapp-staging",
            "DB_HOST": "stg-db",
            "DB_PORT": "5432",
        },
        "development": {
            "APP_NAME": "myapp-dev",
            "DB_HOST": "localhost",
            "SECRET_KEY": "devkey",
            "DB_PORT": "5432",
        },
    }


def test_calculate_returns_report(checker, three_envs):
    report = checker.calculate(three_envs)
    assert isinstance(report, SortingReport)


def test_env_names_captured(checker, three_envs):
    report = checker.calculate(three_envs)
    assert set(report.env_names) == {"production", "staging", "development"}


def test_sorted_env_detected(checker, three_envs):
    report = checker.calculate(three_envs)
    prod = next(e for e in report.envs if e.name == "production")
    assert prod.is_sorted is True


def test_unsorted_env_detected(checker, three_envs):
    report = checker.calculate(three_envs)
    staging = next(e for e in report.envs if e.name == "staging")
    assert staging.is_sorted is False


def test_has_unsorted_true_when_any_unsorted(checker, three_envs):
    report = checker.calculate(three_envs)
    assert report.has_unsorted is True


def test_has_unsorted_false_when_all_sorted(checker):
    envs = {
        "a": {"ALPHA": "1", "BETA": "2", "GAMMA": "3"},
        "b": {"ALPHA": "x", "BETA": "y", "GAMMA": "z"},
    }
    report = checker.calculate(envs)
    assert report.has_unsorted is False


def test_unsorted_envs_list(checker, three_envs):
    report = checker.calculate(three_envs)
    names = [e.name for e in report.unsorted_envs]
    assert "staging" in names
    assert "production" not in names


def test_suggest_sorted_returns_alphabetical_order(checker):
    env = {"ZEBRA": "z", "APPLE": "a", "MANGO": "m"}
    result = checker.suggest_sorted(env)
    assert list(result.keys()) == ["APPLE", "MANGO", "ZEBRA"]


def test_sorted_env_str(checker):
    env = SortedEnv(name="prod", keys=["A", "B"], original_order=["A", "B"])
    assert "sorted" in str(env)
    assert "prod" in str(env)


def test_unsorted_env_str(checker):
    env = SortedEnv(name="dev", keys=["A", "B"], original_order=["B", "A"])
    assert "unsorted" in str(env)
