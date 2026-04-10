"""Tests for envdiff.filter_cli."""

import argparse
import pytest

from envdiff.filter_cli import (
    add_filter_arguments,
    apply_filter_to_envs,
    build_filter_from_args,
)
from envdiff.key_filter import KeyFilter, KeyFilterConfig


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    add_filter_arguments(p)
    return p


def test_add_filter_arguments_registers_flags(parser):
    args = parser.parse_args([])
    assert hasattr(args, "include")
    assert hasattr(args, "exclude")
    assert hasattr(args, "prefixes")


def test_defaults_are_empty_lists(parser):
    args = parser.parse_args([])
    assert args.include == []
    assert args.exclude == []
    assert args.prefixes == []


def test_include_flag_parsed(parser):
    args = parser.parse_args(["--include", "APP_*", "DB_*"])
    assert args.include == ["APP_*", "DB_*"]


def test_exclude_flag_parsed(parser):
    args = parser.parse_args(["--exclude", "*SECRET*"])
    assert args.exclude == ["*SECRET*"]


def test_prefix_flag_parsed(parser):
    args = parser.parse_args(["--prefix", "APP_", "DB_"])
    assert args.prefixes == ["APP_", "DB_"]


def test_build_filter_from_args_returns_key_filter(parser):
    args = parser.parse_args(["--include", "APP_*"])
    kf = build_filter_from_args(args)
    assert isinstance(kf, KeyFilter)


def test_build_filter_applies_correctly(parser):
    args = parser.parse_args(["--prefix", "APP_"])
    kf = build_filter_from_args(args)
    env = {"APP_NAME": "x", "DB_HOST": "h"}
    assert kf.apply(env) == {"APP_NAME": "x"}


def test_apply_filter_to_envs_filters_all():
    kf = KeyFilter(KeyFilterConfig(prefixes=["APP_"]))
    envs = {
        "staging": {"APP_NAME": "s", "DB_HOST": "h"},
        "prod": {"APP_NAME": "p", "LOG_LEVEL": "warn"},
    }
    result = apply_filter_to_envs(envs, kf)
    assert result == {
        "staging": {"APP_NAME": "s"},
        "prod": {"APP_NAME": "p"},
    }


def test_apply_filter_to_envs_empty_input():
    kf = KeyFilter()
    assert apply_filter_to_envs({}, kf) == {}
