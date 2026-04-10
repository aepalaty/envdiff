"""Tests for envdiff.key_filter."""

import pytest
from envdiff.key_filter import KeyFilter, KeyFilterConfig


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "APP_DEBUG": "true",
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "AWS_ACCESS_KEY_ID": "AKIA123",
        "AWS_SECRET_ACCESS_KEY": "abc",
        "LOG_LEVEL": "info",
    }


def test_no_filter_returns_all_keys(sample_env):
    kf = KeyFilter()
    result = kf.apply(sample_env)
    assert result == sample_env


def test_prefix_filter_limits_keys(sample_env):
    cfg = KeyFilterConfig(prefixes=["APP_"])
    kf = KeyFilter(cfg)
    result = kf.apply(sample_env)
    assert set(result.keys()) == {"APP_NAME", "APP_DEBUG"}


def test_multiple_prefixes(sample_env):
    cfg = KeyFilterConfig(prefixes=["DB_", "AWS_"])
    kf = KeyFilter(cfg)
    result = kf.apply(sample_env)
    assert set(result.keys()) == {"DB_HOST", "DB_PASSWORD", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"}


def test_include_glob_pattern(sample_env):
    cfg = KeyFilterConfig(include_patterns=["DB_*"])
    kf = KeyFilter(cfg)
    result = kf.apply(sample_env)
    assert set(result.keys()) == {"DB_HOST", "DB_PASSWORD"}


def test_exclude_glob_pattern(sample_env):
    cfg = KeyFilterConfig(exclude_patterns=["*PASSWORD*", "*SECRET*"])
    kf = KeyFilter(cfg)
    result = kf.apply(sample_env)
    assert "DB_PASSWORD" not in result
    assert "AWS_SECRET_ACCESS_KEY" not in result
    assert "APP_NAME" in result


def test_include_and_exclude_combined(sample_env):
    cfg = KeyFilterConfig(
        include_patterns=["AWS_*"],
        exclude_patterns=["*SECRET*"],
    )
    kf = KeyFilter(cfg)
    result = kf.apply(sample_env)
    assert set(result.keys()) == {"AWS_ACCESS_KEY_ID"}


def test_filter_keys_returns_list(sample_env):
    cfg = KeyFilterConfig(prefixes=["LOG_"])
    kf = KeyFilter(cfg)
    keys = kf.filter_keys(list(sample_env.keys()))
    assert keys == ["LOG_LEVEL"]


def test_from_dict_parses_config():
    data = {
        "include": ["APP_*"],
        "exclude": ["APP_DEBUG"],
        "prefixes": ["APP_"],
    }
    cfg = KeyFilterConfig.from_dict(data)
    kf = KeyFilter(cfg)
    env = {"APP_NAME": "x", "APP_DEBUG": "true", "DB_HOST": "h"}
    result = kf.apply(env)
    assert result == {"APP_NAME": "x"}


def test_empty_env_returns_empty():
    kf = KeyFilter(KeyFilterConfig(prefixes=["APP_"]))
    assert kf.apply({}) == {}
