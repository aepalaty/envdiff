"""Tests for key collision detection."""
import pytest
from envdiff.key_collisions import KeyCollisionDetector, CollisionReport, CollisionEntry


@pytest.fixture
def detector():
    return KeyCollisionDetector()


@pytest.fixture
def clean_envs():
    return {
        "prod": {"DB_HOST": "prod-db", "APP_PORT": "8080"},
        "staging": {"DB_HOST": "staging-db", "APP_PORT": "9090"},
    }


@pytest.fixture
def colliding_envs():
    return {
        "prod": {"DB_HOST": "prod-db", "API_KEY": "abc"},
        "staging": {"db_host": "staging-db", "Api_Key": "xyz"},
    }


def test_calculate_returns_report(detector, clean_envs):
    report = detector.calculate(clean_envs)
    assert isinstance(report, CollisionReport)


def test_env_names_captured(detector, clean_envs):
    report = detector.calculate(clean_envs)
    assert "prod" in report.env_names
    assert "staging" in report.env_names


def test_no_collisions_in_clean_envs(detector, clean_envs):
    report = detector.calculate(clean_envs)
    assert not report.has_collisions
    assert report.collision_keys == []


def test_detects_case_collision(detector, colliding_envs):
    report = detector.calculate(colliding_envs)
    assert report.has_collisions


def test_collision_keys_are_lowercase_canonical(detector, colliding_envs):
    report = detector.calculate(colliding_envs)
    assert "db_host" in report.collision_keys
    assert "api_key" in report.collision_keys


def test_collision_entry_has_variants(detector, colliding_envs):
    report = detector.calculate(colliding_envs)
    db_entry = next(e for e in report.entries if e.canonical == "db_host")
    assert "DB_HOST" in db_entry.variants
    assert "db_host" in db_entry.variants


def test_collision_entry_has_envs(detector, colliding_envs):
    report = detector.calculate(colliding_envs)
    db_entry = next(e for e in report.entries if e.canonical == "db_host")
    assert "prod" in db_entry.envs
    assert "staging" in db_entry.envs


def test_entries_sorted_by_canonical(detector, colliding_envs):
    report = detector.calculate(colliding_envs)
    canonicals = [e.canonical for e in report.entries]
    assert canonicals == sorted(canonicals)


def test_str_representation(detector, colliding_envs):
    report = detector.calculate(colliding_envs)
    entry = report.entries[0]
    result = str(entry)
    assert entry.canonical in result


def test_single_env_no_collision(detector):
    envs = {"only": {"KEY_ONE": "a", "KEY_TWO": "b"}}
    report = detector.calculate(envs)
    assert not report.has_collisions
