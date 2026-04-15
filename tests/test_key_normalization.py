"""Tests for envdiff.key_normalization."""
import pytest
from envdiff.key_normalization import (
    KeyNormalizationDetector,
    NormalizationGroup,
    NormalizationReport,
    _normalize,
)


@pytest.fixture
def detector():
    return KeyNormalizationDetector()


@pytest.fixture
def mixed_envs():
    return {
        "dev": {"DB_URL": "postgres://dev", "API-KEY": "abc", "app.name": "myapp"},
        "prod": {"DB_URL": "postgres://prod", "API_KEY": "xyz", "APP_NAME": "myapp"},
        "staging": {"DB_URL": "postgres://staging", "api_key": "def"},
    }


def test_normalize_hyphens():
    assert _normalize("API-KEY") == "api_key"


def test_normalize_dots():
    assert _normalize("app.name") == "app_name"


def test_normalize_already_clean():
    assert _normalize("DB_URL") == "db_url"


def test_normalize_mixed():
    assert _normalize("My-App.Name") == "my_app_name"


def test_detect_returns_report(detector, mixed_envs):
    report = detector.detect(mixed_envs)
    assert isinstance(report, NormalizationReport)


def test_env_names_captured(detector, mixed_envs):
    report = detector.detect(mixed_envs)
    assert set(report.env_names) == {"dev", "prod", "staging"}


def test_api_key_variants_grouped(detector, mixed_envs):
    report = detector.detect(mixed_envs)
    api_group = next(
        (g for g in report.groups if g.canonical == "api_key"), None
    )
    assert api_group is not None
    assert set(api_group.variants) == {"API-KEY", "API_KEY", "api_key"}


def test_app_name_variants_grouped(detector, mixed_envs):
    report = detector.detect(mixed_envs)
    app_group = next(
        (g for g in report.groups if g.canonical == "app_name"), None
    )
    assert app_group is not None
    assert set(app_group.variants) == {"app.name", "APP_NAME"}


def test_unique_key_has_no_conflict(detector, mixed_envs):
    report = detector.detect(mixed_envs)
    db_group = next(
        (g for g in report.groups if g.canonical == "db_url"), None
    )
    assert db_group is not None
    assert len(db_group) == 1


def test_has_conflicts_true(detector, mixed_envs):
    report = detector.detect(mixed_envs)
    assert report.has_conflicts is True


def test_has_conflicts_false(detector):
    clean = {
        "dev": {"DB_URL": "a", "API_KEY": "b"},
        "prod": {"DB_URL": "c", "API_KEY": "d"},
    }
    report = detector.detect(clean)
    assert report.has_conflicts is False


def test_conflict_groups_only_returns_multi_variant(detector, mixed_envs):
    report = detector.detect(mixed_envs)
    for g in report.conflict_groups:
        assert len(g) > 1


def test_empty_envs_returns_empty_report(detector):
    report = detector.detect({})
    assert report.groups == []
    assert report.has_conflicts is False
