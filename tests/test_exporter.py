"""Tests for envdiff.exporter.DiffExporter."""

import csv
import io
import json

import pytest

from envdiff.comparator import EnvDifference
from envdiff.exporter import DiffExporter


@pytest.fixture()
def diff_a() -> EnvDifference:
    return EnvDifference(
        baseline_file=".env.prod",
        other_file=".env.staging",
        missing_keys={"SECRET_KEY"},
        extra_keys={"DEBUG"},
        mismatched_keys={"DATABASE_URL"},
    )


@pytest.fixture()
def diff_b() -> EnvDifference:
    return EnvDifference(
        baseline_file=".env.prod",
        other_file=".env.dev",
        missing_keys=set(),
        extra_keys=set(),
        mismatched_keys=set(),
    )


@pytest.fixture()
def exporter(diff_a, diff_b) -> DiffExporter:
    return DiffExporter([diff_a, diff_b])


def test_to_json_structure(exporter):
    result = json.loads(exporter.to_json())
    assert isinstance(result, list)
    assert len(result) == 2
    first = result[0]
    assert first["baseline"] == ".env.prod"
    assert first["other"] == ".env.staging"
    assert "SECRET_KEY" in first["missing_keys"]
    assert "DEBUG" in first["extra_keys"]
    assert "DATABASE_URL" in first["mismatched_keys"]


def test_to_json_empty_diff(diff_b):
    result = json.loads(DiffExporter([diff_b]).to_json())
    assert result[0]["missing_keys"] == []
    assert result[0]["extra_keys"] == []
    assert result[0]["mismatched_keys"] == []


def test_to_csv_headers(exporter):
    raw = exporter.to_csv()
    reader = csv.reader(io.StringIO(raw))
    headers = next(reader)
    assert headers == ["baseline", "other", "issue_type", "key"]


def test_to_csv_rows(exporter):
    raw = exporter.to_csv()
    rows = list(csv.reader(io.StringIO(raw)))[1:]  # skip header
    issue_types = {row[2] for row in rows}
    assert "missing" in issue_types
    assert "extra" in issue_types
    assert "mismatch" in issue_types


def test_to_markdown_contains_headers(exporter):
    md = exporter.to_markdown()
    assert "| Issue Type | Key |" in md
    assert "|------------|-----|" in md


def test_to_markdown_contains_keys(exporter):
    md = exporter.to_markdown()
    assert "`SECRET_KEY`" in md
    assert "`DEBUG`" in md
    assert "`DATABASE_URL`" in md


def test_export_dispatch_json(exporter):
    result = exporter.export("json")
    assert json.loads(result)  # valid JSON


def test_export_dispatch_csv(exporter):
    result = exporter.export("csv")
    assert "baseline" in result


def test_export_dispatch_markdown(exporter):
    result = exporter.export("markdown")
    assert "##" in result


def test_export_unsupported_format_raises(exporter):
    with pytest.raises(ValueError, match="Unsupported export format"):
        exporter.export("xml")
