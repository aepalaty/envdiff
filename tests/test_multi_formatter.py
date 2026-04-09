"""Tests for MultiDiffFormatter."""

import pytest

from envdiff.comparator import EnvDifference
from envdiff.differ import MultiDiffResult, PairwiseDiff
from envdiff.multi_formatter import MultiDiffFormatter


@pytest.fixture
def formatter():
    return MultiDiffFormatter(color=False)


@pytest.fixture
def clean_diff():
    diff = EnvDifference(baseline="a.env", other="b.env")
    return PairwiseDiff(left_path="a.env", right_path="b.env", difference=diff)


@pytest.fixture
def dirty_diff():
    diff = EnvDifference(
        baseline="a.env",
        other="b.env",
        missing_keys=["KEY_X"],
        mismatched_values={"KEY_Y": ("old", "new")},
    )
    return PairwiseDiff(left_path="a.env", right_path="b.env", difference=diff)


def test_format_all_empty_returns_message(formatter):
    result = MultiDiffResult(paths=[])
    output = formatter.format_all(result)
    assert "No comparisons" in output


def test_format_all_includes_header(formatter, clean_diff):
    result = MultiDiffResult(paths=["a.env", "b.env"], pairwise=[clean_diff])
    output = formatter.format_all(result)
    assert "a.env" in output
    assert "b.env" in output


def test_format_all_multiple_pairs(formatter, clean_diff, dirty_diff):
    result = MultiDiffResult(
        paths=["a.env", "b.env", "c.env"],
        pairwise=[clean_diff, dirty_diff],
    )
    output = formatter.format_all(result)
    assert output.count("---") >= 2


def test_format_summary_no_issues(formatter, clean_diff):
    result = MultiDiffResult(paths=["a.env", "b.env"], pairwise=[clean_diff])
    summary = formatter.format_summary(result)
    assert "All files are in sync" in summary


def test_format_summary_with_issues(formatter, dirty_diff):
    result = MultiDiffResult(paths=["a.env", "b.env"], pairwise=[dirty_diff])
    summary = formatter.format_summary(result)
    assert "1/1" in summary
    assert "Unique differing keys" in summary


def test_format_summary_counts_files(formatter, clean_diff, dirty_diff):
    result = MultiDiffResult(
        paths=["a.env", "b.env", "c.env"],
        pairwise=[clean_diff, dirty_diff],
    )
    summary = formatter.format_summary(result)
    assert "3 file(s)" in summary
    assert "2 pair(s)" in summary
