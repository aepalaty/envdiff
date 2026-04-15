"""Tests for key mutation detection across snapshots."""
import pytest

from envdiff.key_mutations import MutationCalculator, MutationReport
from envdiff.mutation_formatter import MutationFormatter


@pytest.fixture
def calculator():
    return MutationCalculator()


@pytest.fixture
def formatter():
    return MutationFormatter(color=False)


@pytest.fixture
def snapshots():
    return [
        ("v1", {"DB_URL": "postgres://localhost/dev", "SECRET": "abc", "PORT": "5432"}),
        ("v2", {"DB_URL": "postgres://prod/main", "SECRET": "abc", "PORT": "5432"}),
        ("v3", {"DB_URL": "postgres://prod/main", "SECRET": "xyz", "PORT": "8080"}),
    ]


def test_calculate_returns_report(calculator, snapshots):
    report = calculator.calculate(snapshots)
    assert isinstance(report, MutationReport)


def test_all_keys_collected(calculator, snapshots):
    report = calculator.calculate(snapshots)
    keys = {e.key for e in report.entries}
    assert "DB_URL" in keys
    assert "SECRET" in keys
    assert "PORT" in keys


def test_stable_key_has_no_mutations(calculator, snapshots):
    report = calculator.calculate(snapshots)
    secret_entry = next(e for e in report.entries if e.key == "SECRET")
    # SECRET changes in v3
    assert secret_entry.mutation_count == 1


def test_db_url_mutated_in_v2(calculator, snapshots):
    report = calculator.calculate(snapshots)
    db_entry = next(e for e in report.entries if e.key == "DB_URL")
    assert db_entry.has_mutations
    assert db_entry.mutations[0].snapshot_label == "v2"
    assert db_entry.mutations[0].old_value == "postgres://localhost/dev"
    assert db_entry.mutations[0].new_value == "postgres://prod/main"


def test_port_mutated_in_v3(calculator, snapshots):
    report = calculator.calculate(snapshots)
    port_entry = next(e for e in report.entries if e.key == "PORT")
    assert port_entry.mutation_count == 1
    assert port_entry.mutations[0].snapshot_label == "v3"


def test_total_mutations_count(calculator, snapshots):
    report = calculator.calculate(snapshots)
    assert report.total_mutations == 3  # DB_URL(1) + SECRET(1) + PORT(1)


def test_mutated_keys_list(calculator, snapshots):
    report = calculator.calculate(snapshots)
    assert set(report.mutated_keys) == {"DB_URL", "SECRET", "PORT"}


def test_empty_snapshots_returns_empty_report(calculator):
    report = calculator.calculate([])
    assert report.entries == []
    assert report.total_mutations == 0


def test_key_absent_then_added_counts_as_mutation(calculator):
    snaps = [
        ("v1", {"A": "1"}),
        ("v2", {"A": "1", "B": "hello"}),
    ]
    report = calculator.calculate(snaps)
    b_entry = next(e for e in report.entries if e.key == "B")
    assert b_entry.has_mutations
    assert b_entry.mutations[0].old_value is None
    assert b_entry.mutations[0].new_value == "hello"


def test_key_removed_counts_as_mutation(calculator):
    snaps = [
        ("v1", {"A": "1", "B": "bye"}),
        ("v2", {"A": "1"}),
    ]
    report = calculator.calculate(snaps)
    b_entry = next(e for e in report.entries if e.key == "B")
    assert b_entry.has_mutations
    assert b_entry.mutations[0].new_value is None


def test_formatter_format_report_no_color(calculator, formatter, snapshots):
    report = calculator.calculate(snapshots)
    output = formatter.format_report(report)
    assert "Key Mutation Report" in output
    assert "DB_URL" in output
    assert "mutation" in output


def test_formatter_summary_shows_counts(calculator, formatter, snapshots):
    report = calculator.calculate(snapshots)
    summary = formatter.format_summary(report)
    assert "Mutated keys" in summary
    assert "Stable keys" in summary
    assert "Total changes" in summary


def test_formatter_empty_report(formatter):
    report = MutationReport()
    output = formatter.format_report(report)
    assert "No snapshot data" in output
