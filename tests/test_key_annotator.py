"""Tests for key_annotator and annotation_formatter."""
import pytest
from envdiff.key_annotator import KeyAnnotator, KeyAnnotation, AnnotationReport
from envdiff.annotation_formatter import AnnotationFormatter


@pytest.fixture
def annotator():
    return KeyAnnotator()


@pytest.fixture
def formatter():
    return AnnotationFormatter(use_color=False)


SAMPLE_LINES = [
    "# a comment\n",
    "\n",
    "DB_HOST=localhost\n",
    "DB_PORT=5432\n",
    "SECRET_KEY=\n",
    'API_TOKEN="abc123"\n',
    "export EXPORT_VAR=hello\n",
]


def test_annotator_skips_comments_and_blank_lines(annotator):
    report = annotator.annotate("test.env", SAMPLE_LINES)
    keys = [a.key for a in report.annotations]
    assert "#" not in "".join(keys)
    assert len(keys) == 5


def test_annotator_captures_correct_line_numbers(annotator):
    report = annotator.annotate("test.env", SAMPLE_LINES)
    db_host = report.by_key("DB_HOST")
    assert db_host is not None
    assert db_host.line_number == 3


def test_annotator_marks_empty_value(annotator):
    report = annotator.annotate("test.env", SAMPLE_LINES)
    secret = report.by_key("SECRET_KEY")
    assert secret is not None
    assert not secret.has_value
    assert secret.value is None


def test_annotator_strips_quotes(annotator):
    report = annotator.annotate("test.env", SAMPLE_LINES)
    token = report.by_key("API_TOKEN")
    assert token is not None
    assert token.value == "abc123"
    assert token.has_value


def test_annotator_handles_export_prefix(annotator):
    report = annotator.annotate("test.env", SAMPLE_LINES)
    export_var = report.by_key("EXPORT_VAR")
    assert export_var is not None
    assert export_var.value == "hello"


def test_report_populated_and_empty_counts(annotator):
    report = annotator.annotate("test.env", SAMPLE_LINES)
    assert len(report.empty_keys) == 1
    assert len(report.populated_keys) == 4


def test_annotation_str(annotator):
    report = annotator.annotate("test.env", SAMPLE_LINES)
    db = report.by_key("DB_HOST")
    result = str(db)
    assert "DB_HOST" in result
    assert "set" in result
    assert "test.env" in result


def test_formatter_report_includes_env_name(annotator, formatter):
    report = annotator.annotate("staging.env", SAMPLE_LINES)
    output = formatter.format_report(report)
    assert "staging.env" in output


def test_formatter_report_shows_counts(annotator, formatter):
    report = annotator.annotate("staging.env", SAMPLE_LINES)
    output = formatter.format_report(report)
    assert "Total keys" in output
    assert "5" in output


def test_formatter_summary_includes_all_reports(annotator, formatter):
    r1 = annotator.annotate("dev.env", SAMPLE_LINES)
    r2 = annotator.annotate("prod.env", ["KEY=value\n"])
    output = formatter.format_summary([r1, r2])
    assert "dev.env" in output
    assert "prod.env" in output


def test_formatter_empty_env(formatter):
    report = AnnotationReport(env_name="empty.env")
    output = formatter.format_report(report)
    assert "no keys found" in output
