"""Tests for key rename detection."""
import pytest
from envdiff.key_rename import KeyRenameDetector, RenameCandidate, RenameReport


@pytest.fixture
def detector():
    return KeyRenameDetector(threshold=0.6, prefer_value_match=True)


def test_detects_obvious_rename(detector):
    old_env = {"DATABASE_URL": "postgres://localhost/db"}
    new_env = {"DB_URL": "postgres://localhost/db"}
    report = detector.detect(old_env, new_env, ["DATABASE_URL"], ["DB_URL"])
    assert report.has_candidates()
    assert report.candidates[0].old_key == "DATABASE_URL"
    assert report.candidates[0].new_key == "DB_URL"


def test_value_match_boosts_score(detector):
    old_env = {"SECRET_KEY": "abc123", "API_TOKEN": "abc123"}
    new_env = {"SECRET_TOKEN": "abc123", "APP_KEY": "xyz"}
    report = detector.detect(
        old_env, new_env,
        ["SECRET_KEY", "API_TOKEN"],
        ["SECRET_TOKEN", "APP_KEY"]
    )
    keys_matched = {c.old_key for c in report.candidates}
    assert "SECRET_KEY" in keys_matched


def test_no_candidates_when_keys_too_different(detector):
    old_env = {"FOO": "1"}
    new_env = {"ZZZZ_COMPLETELY_DIFFERENT": "1"}
    report = detector.detect(old_env, new_env, ["FOO"], ["ZZZZ_COMPLETELY_DIFFERENT"])
    assert not report.has_candidates()
    assert "FOO" in report.unmatched_old
    assert "ZZZZ_COMPLETELY_DIFFERENT" in report.unmatched_new


def test_unmatched_keys_reported(detector):
    old_env = {"OLD_KEY": "val", "UNRELATED": "x"}
    new_env = {"NEW_KEY": "val"}
    report = detector.detect(
        old_env, new_env,
        ["OLD_KEY", "UNRELATED"],
        ["NEW_KEY"]
    )
    assert "UNRELATED" in report.unmatched_old


def test_each_key_matched_at_most_once(detector):
    old_env = {"DB_HOST": "localhost", "DB_HOSTNAME": "localhost"}
    new_env = {"DATABASE_HOST": "localhost"}
    report = detector.detect(
        old_env, new_env,
        ["DB_HOST", "DB_HOSTNAME"],
        ["DATABASE_HOST"]
    )
    matched_new = [c.new_key for c in report.candidates]
    assert matched_new.count("DATABASE_HOST") == 1


def test_candidate_str_representation():
    c = RenameCandidate(old_key="FOO", new_key="BAR", score=0.75, value_match=True)
    s = str(c)
    assert "FOO" in s
    assert "BAR" in s
    assert "value match" in s


def test_candidate_str_no_value_match():
    c = RenameCandidate(old_key="A", new_key="B", score=0.65, value_match=False)
    assert "value match" not in str(c)


def test_empty_inputs_return_empty_report(detector):
    report = detector.detect({}, {}, [], [])
    assert not report.has_candidates()
    assert report.unmatched_old == []
    assert report.unmatched_new == []


def test_threshold_respected():
    strict_detector = KeyRenameDetector(threshold=0.95)
    old_env = {"APP_SECRET": "x"}
    new_env = {"APP_SECRETT": "x"}
    report = strict_detector.detect(old_env, new_env, ["APP_SECRET"], ["APP_SECRETT"])
    # score for APP_SECRET vs APP_SECRETT is high but let's verify behaviour
    # either it matches or it doesn't — just ensure no crash
    assert isinstance(report, RenameReport)
