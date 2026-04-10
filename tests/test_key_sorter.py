"""Tests for envdiff.key_sorter."""

import pytest

from envdiff.key_sorter import KeyGroup, KeySorter


@pytest.fixture
def sorter() -> KeySorter:
    return KeySorter()


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_KEY": "abc",
        "AWS_SECRET": "xyz",
        "PORT": "8080",
        "DEBUG": "true",
    }


def test_group_by_prefix_returns_key_groups(sorter, sample_env):
    groups = sorter.group_by_prefix(sample_env)
    assert all(isinstance(g, KeyGroup) for g in groups)


def test_group_by_prefix_correct_labels(sorter, sample_env):
    groups = sorter.group_by_prefix(sample_env)
    labels = [g.name for g in groups]
    assert "AWS" in labels
    assert "DB" in labels
    assert "OTHER" in labels


def test_group_by_prefix_groups_are_sorted(sorter, sample_env):
    groups = sorter.group_by_prefix(sample_env)
    labels = [g.name for g in groups]
    assert labels == sorted(labels)


def test_group_by_prefix_keys_within_group_sorted(sorter, sample_env):
    groups = sorter.group_by_prefix(sample_env)
    db_group = next(g for g in groups if g.name == "DB")
    keys = list(db_group.keys)
    assert keys == sorted(keys)


def test_group_by_prefix_ungrouped_keys_in_other(sorter, sample_env):
    groups = sorter.group_by_prefix(sample_env)
    other = next(g for g in groups if g.name == "OTHER")
    assert "PORT" in other.keys
    assert "DEBUG" in other.keys


def test_sort_flat_returns_sorted_dict(sorter, sample_env):
    result = sorter.sort_flat(sample_env)
    keys = list(result)
    assert keys == sorted(keys)


def test_sort_flat_preserves_values(sorter, sample_env):
    result = sorter.sort_flat(sample_env)
    for key, value in sample_env.items():
        assert result[key] == value


def test_sort_keys_list(sorter):
    keys = ["ZEBRA", "ALPHA", "MIDDLE"]
    assert sorter.sort_keys_list(keys) == ["ALPHA", "MIDDLE", "ZEBRA"]


def test_split_by_prefix_returns_tuples(sorter):
    keys = ["DB_HOST", "DB_PORT", "AWS_KEY", "PORT"]
    result = sorter.split_by_prefix(keys)
    assert isinstance(result, list)
    assert all(isinstance(t, tuple) and len(t) == 2 for t in result)


def test_split_by_prefix_correct_grouping(sorter):
    keys = ["DB_HOST", "DB_PORT", "AWS_KEY"]
    result = dict(sorter.split_by_prefix(keys))
    assert "DB" in result
    assert "DB_HOST" in result["DB"]
    assert "DB_PORT" in result["DB"]
    assert "AWS_KEY" in result["AWS"]


def test_custom_ungrouped_label():
    sorter = KeySorter(ungrouped_label="MISC")
    result = sorter.group_by_prefix({"PORT": "8080"})
    assert result[0].name == "MISC"


def test_empty_env(sorter):
    assert sorter.group_by_prefix({}) == []
    assert sorter.sort_flat({}) == {}
    assert sorter.sort_keys_list([]) == []
