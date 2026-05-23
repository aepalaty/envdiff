import pytest
from envdiff.key_ownership import OwnershipCalculator, OwnershipReport, OwnershipEntry
from envdiff.ownership_formatter import OwnershipFormatter


REGISTRY = {
    "DATABASE_URL": {"owner": "alice", "team": "backend", "contact": "alice@example.com"},
    "SECRET_KEY": {"owner": "bob", "team": "security"},
}

SAMPLE_ENV = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "supersecret",
    "APP_NAME": "myapp",
}


@pytest.fixture
def calculator():
    return OwnershipCalculator(registry=REGISTRY)


@pytest.fixture
def formatter():
    return OwnershipFormatter(use_color=False)


def test_calculate_returns_report(calculator):
    report = calculator.calculate(SAMPLE_ENV)
    assert isinstance(report, OwnershipReport)


def test_all_keys_present(calculator):
    report = calculator.calculate(SAMPLE_ENV)
    keys = [e.key for e in report.entries]
    assert "DATABASE_URL" in keys
    assert "SECRET_KEY" in keys
    assert "APP_NAME" in keys


def test_owned_key_has_owner(calculator):
    report = calculator.calculate(SAMPLE_ENV)
    entry = next(e for e in report.entries if e.key == "DATABASE_URL")
    assert entry.owner == "alice"
    assert entry.team == "backend"
    assert entry.contact == "alice@example.com"
    assert not entry.is_unowned


def test_unowned_key_flagged(calculator):
    report = calculator.calculate(SAMPLE_ENV)
    entry = next(e for e in report.entries if e.key == "APP_NAME")
    assert entry.is_unowned
    assert entry.owner is None
    assert entry.team is None


def test_unowned_keys_list(calculator):
    report = calculator.calculate(SAMPLE_ENV)
    assert "APP_NAME" in report.unowned_keys
    assert "DATABASE_URL" not in report.unowned_keys


def test_owned_keys_list(calculator):
    report = calculator.calculate(SAMPLE_ENV)
    assert "DATABASE_URL" in report.owned_keys
    assert "SECRET_KEY" in report.owned_keys
    assert "APP_NAME" not in report.owned_keys


def test_has_unowned_true(calculator):
    report = calculator.calculate(SAMPLE_ENV)
    assert report.has_unowned is True


def test_has_unowned_false(calculator):
    fully_owned = {"DATABASE_URL": "x", "SECRET_KEY": "y"}
    report = calculator.calculate(fully_owned)
    assert report.has_unowned is False


def test_format_report_includes_key_names(calculator, formatter):
    report = calculator.calculate(SAMPLE_ENV)
    output = formatter.format_report(report)
    assert "DATABASE_URL" in output
    assert "APP_NAME" in output


def test_format_report_marks_unowned(calculator, formatter):
    report = calculator.calculate(SAMPLE_ENV)
    output = formatter.format_report(report)
    assert "UNOWNED" in output


def test_format_report_shows_owner(calculator, formatter):
    report = calculator.calculate(SAMPLE_ENV)
    output = formatter.format_report(report)
    assert "alice" in output


def test_entry_str_unowned():
    entry = OwnershipEntry(key="FOO", owner=None, team=None, contact=None)
    assert str(entry) == "FOO"


def test_entry_str_with_owner():
    entry = OwnershipEntry(key="BAR", owner="carol", team="ops", contact=None)
    result = str(entry)
    assert "owner=carol" in result
    assert "team=ops" in result
