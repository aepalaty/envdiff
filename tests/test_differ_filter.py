"""Tests for DiffFilter utility."""

import pytest
from unittest.mock import MagicMock
from envdiff.differ import MultiDiffResult, PairwiseDiff
from envdiff.comparator import EnvDifference
from envdiff.differ_filter import DiffFilter


def make_diff(other_path, missing=(), extra=(), mismatched=()) -> PairwiseDiff:
    difference = MagicMock(spec=EnvDifference)
    difference.missing_keys = list(missing)
    difference.extra_keys = list(extra)
    difference.mismatched_keys = list(mismatched)
    d = MagicMock(spec=PairwiseDiff)
    d.other_path = other_path
    d.difference = difference
    d.has_issues = bool(missing or extra or mismatched)
    return d


@pytest.fixture
def multi_result():
    diffs = [
        make_diff("staging.env", missing=["DB_HOST", "SECRET"], extra=["LEGACY"]),
        make_diff("prod.env", mismatched=["DB_HOST"], missing=["SECRET"]),
        make_diff("local.env"),  # clean
    ]
    result = MagicMock(spec=MultiDiffResult)
    result.diffs = diffs
    return result


@pytest.fixture
def diff_filter(multi_result):
    return DiffFilter(multi_result)


def test_only_missing_returns_diffs_with_missing_keys(diff_filter):
    result = diff_filter.only_missing()
    assert len(result) == 2
    paths = [d.other_path for d in result]
    assert "staging.env" in paths
    assert "prod.env" in paths


def test_only_mismatched_returns_correct_diffs(diff_filter):
    result = diff_filter.only_mismatched()
    assert len(result) == 1
    assert result[0].other_path == "prod.env"


def test_only_extra_returns_correct_diffs(diff_filter):
    result = diff_filter.only_extra()
    assert len(result) == 1
    assert result[0].other_path == "staging.env"


def test_with_issues_excludes_clean_diffs(diff_filter):
    result = diff_filter.with_issues()
    assert len(result) == 2
    assert all(d.has_issues for d in result)


def test_for_key_returns_diffs_containing_key(diff_filter):
    result = diff_filter.for_key("SECRET")
    assert len(result) == 2


def test_for_key_returns_empty_when_key_not_found(diff_filter):
    result = diff_filter.for_key("NONEXISTENT_KEY")
    assert result == []


def test_keys_always_missing_returns_intersection(diff_filter):
    always = diff_filter.keys_always_missing()
    assert "SECRET" in always
    assert "DB_HOST" not in always  # only missing in staging


def test_keys_sometimes_missing(diff_filter):
    sometimes = diff_filter.keys_sometimes_missing()
    assert "DB_HOST" in sometimes
    assert "SECRET" not in sometimes


def test_summary_by_file_structure(diff_filter):
    summary = diff_filter.summary_by_file()
    assert "staging.env" in summary
    assert summary["staging.env"]["missing"] == 2
    assert summary["staging.env"]["extra"] == 1
    assert summary["local.env"]["has_issues"] is False


def test_empty_multi_result_keys_always_missing():
    result = MagicMock(spec=MultiDiffResult)
    result.diffs = []
    f = DiffFilter(result)
    assert f.keys_always_missing() == set()
