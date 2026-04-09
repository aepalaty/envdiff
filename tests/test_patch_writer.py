"""Tests for envdiff.patch_writer."""

from __future__ import annotations

import pytest

from envdiff.comparator import EnvDifference
from envdiff.patch_writer import PatchWriter


@pytest.fixture()
def clean_diff() -> EnvDifference:
    """A difference with no issues."""
    return EnvDifference(
        baseline_name="prod",
        other_name="staging",
        missing_keys=set(),
        extra_keys=set(),
        mismatched_keys=set(),
        baseline_values={},
        other_values={},
    )


@pytest.fixture()
def dirty_diff() -> EnvDifference:
    return EnvDifference(
        baseline_name="prod",
        other_name="staging",
        missing_keys={"DB_HOST", "SECRET_KEY"},
        extra_keys={"LEGACY_FLAG"},
        mismatched_keys={"LOG_LEVEL"},
        baseline_values={"DB_HOST": "db.prod", "SECRET_KEY": 'p@ss"word', "LOG_LEVEL": "ERROR"},
        other_values={"LOG_LEVEL": "DEBUG", "LEGACY_FLAG": "1"},
    )


def test_render_no_changes_message(clean_diff: EnvDifference) -> None:
    writer = PatchWriter(clean_diff, target_name="staging")
    output = writer.render()
    assert "No changes required" in output


def test_render_contains_missing_keys(dirty_diff: EnvDifference) -> None:
    writer = PatchWriter(dirty_diff, target_name="staging")
    output = writer.render()
    assert 'export DB_HOST="db.prod"' in output
    assert 'export SECRET_KEY=' in output


def test_render_quotes_value_with_embedded_quote(dirty_diff: EnvDifference) -> None:
    writer = PatchWriter(dirty_diff, target_name="staging")
    output = writer.render()
    assert 'export SECRET_KEY="p@ss\\"word"' in output


def test_render_contains_mismatched_keys(dirty_diff: EnvDifference) -> None:
    writer = PatchWriter(dirty_diff, target_name="staging")
    output = writer.render()
    assert 'export LOG_LEVEL="ERROR"' in output


def test_render_header_includes_target_name(dirty_diff: EnvDifference) -> None:
    writer = PatchWriter(dirty_diff, target_name="my-staging")
    output = writer.render()
    assert "my-staging" in output


def test_default_filename(dirty_diff: EnvDifference) -> None:
    writer = PatchWriter(dirty_diff, target_name="staging env")
    assert writer.default_filename() == "envdiff_patch_staging_env.sh"


def test_write_creates_file(tmp_path, dirty_diff: EnvDifference) -> None:
    out_path = tmp_path / "patches" / "staging.sh"
    writer = PatchWriter(dirty_diff, target_name="staging")
    result = writer.write(str(out_path))
    assert result == out_path
    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "export DB_HOST" in content


def test_write_default_filename(tmp_path, dirty_diff: EnvDifference, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    writer = PatchWriter(dirty_diff, target_name="staging")
    result = writer.write()
    assert result.name == "envdiff_patch_staging.sh"
    assert result.exists()
