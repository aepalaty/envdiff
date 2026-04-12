"""Tests for KeyGrouper and GrouperFormatter."""

import pytest

from envdiff.key_grouper import KeyGrouper, GroupReport
from envdiff.grouper_formatter import GrouperFormatter


@pytest.fixture
def grouper():
    return KeyGrouper(min_group_size=2)


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_ACCESS_KEY": "abc",
        "AWS_SECRET": "xyz",
        "PORT": "8080",
        "DEBUG": "true",
    }


def test_groups_by_prefix(grouper, sample_env):
    report = grouper.group(sample_env)
    assert "DB" in report.groups
    assert "AWS" in report.groups


def test_group_contains_correct_keys(grouper, sample_env):
    report = grouper.group(sample_env)
    assert set(report.groups["DB"].keys) == {"DB_HOST", "DB_PORT", "DB_NAME"}
    assert set(report.groups["AWS"].keys) == {"AWS_ACCESS_KEY", "AWS_SECRET"}


def test_ungrouped_keys_captured(grouper, sample_env):
    report = grouper.group(sample_env)
    assert "PORT" in report.ungrouped
    assert "DEBUG" in report.ungrouped


def test_single_key_prefix_not_grouped(grouper):
    env = {"SOLO_KEY": "value", "DB_HOST": "localhost", "DB_PORT": "5432"}
    report = grouper.group(env)
    assert "SOLO" not in report.groups
    assert "SOLO_KEY" in report.ungrouped


def test_min_group_size_respected():
    grouper = KeyGrouper(min_group_size=3)
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "AWS_KEY": "k"}
    report = grouper.group(env)
    assert "DB" not in report.groups
    assert "AWS" not in report.groups
    assert set(report.ungrouped) == {"DB_HOST", "DB_PORT", "AWS_KEY"}


def test_total_grouped_count(grouper, sample_env):
    report = grouper.group(sample_env)
    assert report.total_grouped == 5


def test_group_names_sorted(grouper, sample_env):
    report = grouper.group(sample_env)
    assert report.group_names == sorted(report.group_names)


def test_summary_contains_prefix(grouper, sample_env):
    report = grouper.group(sample_env)
    summary = report.summary()
    assert "[DB]" in summary
    assert "[AWS]" in summary


def test_formatter_includes_group_label(sample_env):
    grouper = KeyGrouper()
    formatter = GrouperFormatter(color=False)
    report = grouper.group(sample_env)
    output = formatter.format_report(report)
    assert "[DB]" in output
    assert "[AWS]" in output


def test_formatter_includes_ungrouped(sample_env):
    grouper = KeyGrouper()
    formatter = GrouperFormatter(color=False)
    report = grouper.group(sample_env)
    output = formatter.format_report(report)
    assert "Ungrouped" in output
    assert "PORT" in output


def test_formatter_no_groups_message():
    grouper = KeyGrouper(min_group_size=10)
    formatter = GrouperFormatter(color=False)
    report = grouper.group({"SOLO": "1"})
    output = formatter.format_report(report)
    assert "No groups found" in output


def test_formatter_env_name_in_header(sample_env):
    grouper = KeyGrouper()
    formatter = GrouperFormatter(color=False)
    report = grouper.group(sample_env)
    output = formatter.format_report(report, env_name="production")
    assert "production" in output
