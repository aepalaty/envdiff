"""Tests for the MultiFileDiffer orchestrator."""

import os
import tempfile

import pytest

from envdiff.differ import MultiFileDiffer, MultiDiffResult, PairwiseDiff


def write_env(content: str) -> str:
    """Write content to a temp file and return its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False)
    f.write(content)
    f.close()
    return f.name


@pytest.fixture(autouse=True)
def cleanup(tmp_files):
    yield
    for path in tmp_files:
        if os.path.exists(path):
            os.unlink(path)


@pytest.fixture
def tmp_files():
    return []


@pytest.fixture
def baseline(tmp_files):
    path = write_env("KEY_A=1\nKEY_B=shared\nKEY_C=only_base\n")
    tmp_files.append(path)
    return path


@pytest.fixture
def other_a(tmp_files):
    path = write_env("KEY_A=1\nKEY_B=shared\n")
    tmp_files.append(path)
    return path


@pytest.fixture
def other_b(tmp_files):
    path = write_env("KEY_A=99\nKEY_B=shared\nKEY_D=extra\n")
    tmp_files.append(path)
    return path


def test_diff_all_returns_multi_result(baseline, other_a, other_b):
    differ = MultiFileDiffer(baseline, [other_a, other_b])
    result = differ.diff_all()
    assert isinstance(result, MultiDiffResult)
    assert len(result.pairwise) == 2


def test_diff_all_detects_missing_key(baseline, other_a):
    differ = MultiFileDiffer(baseline, [other_a])
    result = differ.diff_all()
    pd = result.pairwise[0]
    assert "KEY_C" in pd.difference.extra_keys or "KEY_C" in pd.difference.missing_keys


def test_diff_all_detects_mismatch(baseline, other_b):
    differ = MultiFileDiffer(baseline, [other_b])
    result = differ.diff_all()
    pd = result.pairwise[0]
    assert "KEY_A" in pd.difference.mismatched_values


def test_has_issues_true_when_differences_exist(baseline, other_a):
    differ = MultiFileDiffer(baseline, [other_a])
    result = differ.diff_all()
    assert result.has_issues is True


def test_has_issues_false_when_identical(tmp_files):
    path1 = write_env("KEY=val\n")
    path2 = write_env("KEY=val\n")
    tmp_files.extend([path1, path2])
    differ = MultiFileDiffer(path1, [path2])
    result = differ.diff_all()
    assert result.has_issues is False


def test_diff_all_pairs_covers_all_combinations(baseline, other_a, other_b):
    differ = MultiFileDiffer(baseline, [other_a, other_b])
    result = differ.diff_all_pairs()
    assert len(result.pairwise) == 3  # C(3,2)


def test_all_keys_aggregated(baseline, other_b):
    differ = MultiFileDiffer(baseline, [other_b])
    result = differ.diff_all()
    keys = result.all_keys
    assert isinstance(keys, list)
    assert len(keys) >= 1
