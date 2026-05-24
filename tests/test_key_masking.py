import pytest
from envdiff.key_masking import KeyMasker, MaskingReport, MaskingEntry


@pytest.fixture
def masker() -> KeyMasker:
    return KeyMasker()


@pytest.fixture
def sample_env() -> dict:
    return {
        "DB_PASSWORD": "supersecret",
        "DB_HOST": "localhost",
        "API_KEY": "abc123",
        "APP_NAME": "myapp",
        "AUTH_TOKEN": "tok_xyz",
    }


def test_calculate_returns_report(masker, sample_env):
    report = masker.calculate("prod", sample_env)
    assert isinstance(report, MaskingReport)
    assert report.env_name == "prod"


def test_all_keys_present_in_report(masker, sample_env):
    report = masker.calculate("prod", sample_env)
    assert report.total_keys == len(sample_env)


def test_sensitive_keys_are_masked(masker, sample_env):
    report = masker.calculate("prod", sample_env)
    masked = {e.key: e.masked_value for e in report.entries}
    assert masked["DB_PASSWORD"] == "***"
    assert masked["API_KEY"] == "***"
    assert masked["AUTH_TOKEN"] == "***"


def test_non_sensitive_keys_retain_value(masker, sample_env):
    report = masker.calculate("prod", sample_env)
    masked = {e.key: e.masked_value for e in report.entries}
    assert masked["DB_HOST"] == "localhost"
    assert masked["APP_NAME"] == "myapp"


def test_masked_keys_list(masker, sample_env):
    report = masker.calculate("prod", sample_env)
    assert "DB_PASSWORD" in report.masked_keys
    assert "API_KEY" in report.masked_keys
    assert "DB_HOST" not in report.masked_keys


def test_as_masked_env_returns_dict(masker, sample_env):
    report = masker.calculate("prod", sample_env)
    env = report.as_masked_env()
    assert isinstance(env, dict)
    assert env["DB_PASSWORD"] == "***"
    assert env["APP_NAME"] == "myapp"


def test_empty_sensitive_value_stays_empty(masker):
    env = {"DB_PASSWORD": ""}
    report = masker.calculate("staging", env)
    entry = report.entries[0]
    assert entry.is_sensitive
    assert entry.masked_value == ""


def test_extra_patterns_extend_sensitivity():
    masker = KeyMasker(extra_patterns=["internal"])
    assert masker.is_sensitive("INTERNAL_URL")
    assert not KeyMasker().is_sensitive("INTERNAL_URL")


def test_entry_str_includes_tag(masker):
    entry = MaskingEntry(
        key="DB_PASSWORD",
        original_value="secret",
        masked_value="***",
        is_sensitive=True,
    )
    assert "[sensitive]" in str(entry)
    assert "***" in str(entry)


def test_plain_entry_str_includes_plain_tag(masker):
    entry = MaskingEntry(
        key="APP_NAME",
        original_value="myapp",
        masked_value="myapp",
        is_sensitive=False,
    )
    assert "[plain]" in str(entry)
