import pytest
from envdiff.key_immutability import ImmutabilityChecker, ImmutabilityReport
from envdiff.immutability_formatter import ImmutabilityFormatter


@pytest.fixture
def checker():
    return ImmutabilityChecker(pinned_keys=["APP_VERSION", "ENV_NAME", "REGION"])


@pytest.fixture
def three_snapshots():
    return [
        {"prod": {"APP_VERSION": "1.0", "ENV_NAME": "production", "DB_URL": "db1"}},
        {"prod": {"APP_VERSION": "1.0", "ENV_NAME": "production", "DB_URL": "db2"}},
        {"prod": {"APP_VERSION": "2.0", "ENV_NAME": "production", "DB_URL": "db3"}},
    ]


def test_calculate_returns_report(checker, three_snapshots):
    report = checker.calculate(three_snapshots)
    assert isinstance(report, ImmutabilityReport)


def test_env_names_captured(checker, three_snapshots):
    report = checker.calculate(three_snapshots)
    assert "prod" in report.env_names


def test_stable_key_has_no_violations(checker, three_snapshots):
    report = checker.calculate(three_snapshots)
    issues = report.issues_for_key("ENV_NAME")
    assert len(issues) == 0


def test_changed_pinned_key_flagged(checker, three_snapshots):
    report = checker.calculate(three_snapshots)
    issues = report.issues_for_key("APP_VERSION")
    assert len(issues) == 1
    assert issues[0].old_value == "1.0"
    assert issues[0].new_value == "2.0"


def test_non_pinned_key_not_flagged(checker, three_snapshots):
    report = checker.calculate(three_snapshots)
    issues = report.issues_for_key("DB_URL")
    assert len(issues) == 0


def test_affected_keys_returns_sorted_list(checker, three_snapshots):
    report = checker.calculate(three_snapshots)
    assert report.affected_keys() == sorted(report.affected_keys())


def test_has_issues_true_when_violations(checker, three_snapshots):
    report = checker.calculate(three_snapshots)
    assert report.has_issues() is True


def test_has_issues_false_when_clean(checker):
    snaps = [
        {"prod": {"APP_VERSION": "1.0", "ENV_NAME": "production"}},
        {"prod": {"APP_VERSION": "1.0", "ENV_NAME": "production"}},
    ]
    report = checker.calculate(snaps)
    assert report.has_issues() is False


def test_empty_snapshots_returns_empty_report(checker):
    report = checker.calculate([])
    assert not report.has_issues()
    assert report.env_names == []


def test_custom_labels_used_in_issues(checker):
    snaps = [
        {"prod": {"APP_VERSION": "1.0"}},
        {"prod": {"APP_VERSION": "2.0"}},
    ]
    report = checker.calculate(snaps, labels=["v1", "v2"])
    assert report.issues[0].snapshot_label == "v2"


def test_issue_str_contains_key_and_values(checker):
    snaps = [
        {"prod": {"APP_VERSION": "1.0"}},
        {"prod": {"APP_VERSION": "2.0"}},
    ]
    report = checker.calculate(snaps)
    s = str(report.issues[0])
    assert "APP_VERSION" in s
    assert "1.0" in s
    assert "2.0" in s


def test_formatter_clean_report():
    report = ImmutabilityReport(env_names=["prod"], issues=[])
    fmt = ImmutabilityFormatter(color=False)
    out = fmt.format_report(report)
    assert "No immutability violations" in out


def test_formatter_dirty_report(checker, three_snapshots):
    report = checker.calculate(three_snapshots)
    fmt = ImmutabilityFormatter(color=False)
    out = fmt.format_report(report)
    assert "APP_VERSION" in out


def test_formatter_summary_ok():
    report = ImmutabilityReport(env_names=["prod"], issues=[])
    fmt = ImmutabilityFormatter(color=False)
    assert "ok" in fmt.format_summary(report)
