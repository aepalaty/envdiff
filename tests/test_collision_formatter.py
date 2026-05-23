"""Tests for CollisionFormatter."""
import pytest
from envdiff.key_collisions import KeyCollisionDetector, CollisionEntry, CollisionReport
from envdiff.collision_formatter import CollisionFormatter


@pytest.fixture
def detector():
    return KeyCollisionDetector()


@pytest.fixture
def formatter():
    return CollisionFormatter(color=False)


@pytest.fixture
def clean_report(detector):
    envs = {
        "prod": {"DB_HOST": "prod"},
        "staging": {"DB_HOST": "staging"},
    }
    return detector.calculate(envs)


@pytest.fixture
def dirty_report(detector):
    envs = {
        "prod": {"DB_HOST": "prod", "API_KEY": "abc"},
        "staging": {"db_host": "staging", "api_key": "xyz"},
    }
    return detector.calculate(envs)


def test_format_clean_report_says_no_issues(formatter, clean_report):
    output = formatter.format_report(clean_report)
    assert "No key collisions" in output


def test_format_dirty_report_shows_count(formatter, dirty_report):
    output = formatter.format_report(dirty_report)
    assert "collision" in output.lower()


def test_format_dirty_report_shows_canonical(formatter, dirty_report):
    output = formatter.format_report(dirty_report)
    assert "db_host" in output
    assert "api_key" in output


def test_format_dirty_report_shows_variants(formatter, dirty_report):
    output = formatter.format_report(dirty_report)
    assert "DB_HOST" in output
    assert "db_host" in output


def test_format_dirty_report_shows_envs(formatter, dirty_report):
    output = formatter.format_report(dirty_report)
    assert "prod" in output
    assert "staging" in output


def test_format_summary_clean(formatter, clean_report):
    summary = formatter.format_summary(clean_report)
    assert "none" in summary


def test_format_summary_dirty(formatter, dirty_report):
    summary = formatter.format_summary(dirty_report)
    assert "2" in summary or "key" in summary


def test_format_report_includes_header(formatter, clean_report):
    output = formatter.format_report(clean_report)
    assert "Collision" in output
