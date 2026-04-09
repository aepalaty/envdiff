"""Tests for envdiff.export_writer.ExportWriter."""

import json
from pathlib import Path

import pytest

from envdiff.comparator import EnvDifference
from envdiff.export_writer import ExportWriter


@pytest.fixture()
def single_diff() -> EnvDifference:
    return EnvDifference(
        baseline_file=".env.prod",
        other_file=".env.staging",
        missing_keys={"API_KEY"},
        extra_keys=set(),
        mismatched_keys={"DB_HOST"},
    )


def test_write_json_to_file(tmp_path, single_diff):
    out = tmp_path / "result.json"
    writer = ExportWriter([single_diff], fmt="json", output_path=str(out))
    writer.write()
    data = json.loads(out.read_text())
    assert isinstance(data, list)
    assert data[0]["other"] == ".env.staging"


def test_write_csv_to_file(tmp_path, single_diff):
    out = tmp_path / "result.csv"
    writer = ExportWriter([single_diff], fmt="csv", output_path=str(out))
    writer.write()
    content = out.read_text()
    assert "baseline" in content
    assert "API_KEY" in content


def test_write_markdown_to_file(tmp_path, single_diff):
    out = tmp_path / "result.md"
    writer = ExportWriter([single_diff], fmt="markdown", output_path=str(out))
    writer.write()
    content = out.read_text()
    assert "##" in content
    assert "`API_KEY`" in content


def test_write_creates_parent_dirs(tmp_path, single_diff):
    out = tmp_path / "nested" / "deep" / "result.json"
    writer = ExportWriter([single_diff], fmt="json", output_path=str(out))
    writer.write()
    assert out.exists()


def test_write_to_stdout(capsys, single_diff):
    writer = ExportWriter([single_diff], fmt="json")
    writer.write()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data) == 1


def test_invalid_format_raises():
    with pytest.raises(ValueError, match="Unknown format"):
        ExportWriter([], fmt="xml")


def test_default_filename_json():
    assert ExportWriter.default_filename("json") == "envdiff_report.json"


def test_default_filename_csv():
    assert ExportWriter.default_filename("csv") == "envdiff_report.csv"


def test_default_filename_markdown():
    assert ExportWriter.default_filename("markdown") == "envdiff_report.md"
