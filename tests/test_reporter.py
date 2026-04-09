"""Tests for envdiff.reporter module."""
import json

import pytest

from envdiff.comparator import EnvComparator, EnvDifference
from envdiff.reporter import Report, ReportGenerator


BASELINE = "baseline.env"
TARGET_A = "staging.env"
TARGET_B = "prod.env"


@pytest.fixture()
def generator() -> ReportGenerator:
    return ReportGenerator(BASELINE, [TARGET_A, TARGET_B])


@pytest.fixture()
def diff_a() -> EnvDifference:
    return EnvDifference(
        target_name=TARGET_A,
        missing_keys={"DB_HOST", "SECRET_KEY"},
        extra_keys={"DEBUG"},
        mismatched_keys={"PORT": ("8080", "9090")},
    )


@pytest.fixture()
def diff_b() -> EnvDifference:
    return EnvDifference(
        target_name=TARGET_B,
        missing_keys=set(),
        extra_keys=set(),
        mismatched_keys={},
    )


def test_generate_report_counts(generator, diff_a, diff_b):
    report = generator.generate([diff_a, diff_b])
    # 2 missing + 1 extra + 1 mismatch = 4 issues for staging
    assert report.total_issues == 4
    assert report.has_issues() is True


def test_generate_report_no_issues(generator, diff_b):
    report = generator.generate([diff_b])
    assert report.total_issues == 0
    assert report.has_issues() is False


def test_report_keys_are_sorted(generator, diff_a):
    report = generator.generate([diff_a])
    assert report.missing_keys[TARGET_A] == sorted(["DB_HOST", "SECRET_KEY"])
    assert report.extra_keys[TARGET_A] == ["DEBUG"]
    assert report.mismatched_keys[TARGET_A] == ["PORT"]


def test_to_json_valid(generator, diff_a):
    report = generator.generate([diff_a])
    output = generator.to_json(report)
    parsed = json.loads(output)
    assert parsed["baseline"] == BASELINE
    assert parsed["total_issues"] == 4
    assert TARGET_A in parsed["missing_keys"]


def test_to_text_contains_labels(generator, diff_a):
    report = generator.generate([diff_a])
    text = generator.to_text(report)
    assert "MISSING" in text
    assert "EXTRA" in text
    assert "MISMATCH" in text
    assert TARGET_A in text


def test_to_text_no_issues_omits_target(generator, diff_b):
    report = generator.generate([diff_b])
    text = generator.to_text(report)
    assert TARGET_B not in text
    assert "Total issues: 0" in text


def test_report_baseline_and_targets(generator, diff_a):
    report = generator.generate([diff_a])
    assert report.baseline == BASELINE
    assert TARGET_A in report.targets
    assert TARGET_B in report.targets
