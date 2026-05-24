import pytest
from envdiff.key_anonymization import KeyAnonymizer, AnonymizationReport, _is_sensitive
from envdiff.anonymization_formatter import AnonymizationFormatter


@pytest.fixture
def anonymizer():
    return KeyAnonymizer(method="hash")


@pytest.fixture
def sample_env():
    return {
        "DB_PASSWORD": "supersecret",
        "API_KEY": "myapikey123",
        "APP_NAME": "myapp",
        "PORT": "8080",
        "SECRET_TOKEN": "tok_abc123",
    }


def test_is_sensitive_detects_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_detects_token():
    assert _is_sensitive("SECRET_TOKEN") is True


def test_is_sensitive_ignores_plain_key():
    assert _is_sensitive("APP_NAME") is False
    assert _is_sensitive("PORT") is False


def test_anonymize_returns_report(anonymizer, sample_env):
    report = anonymizer.anonymize("prod", sample_env)
    assert isinstance(report, AnonymizationReport)
    assert report.env_name == "prod"


def test_all_keys_present_in_report(anonymizer, sample_env):
    report = anonymizer.anonymize("prod", sample_env)
    keys = {e.key for e in report.entries}
    assert keys == set(sample_env.keys())


def test_sensitive_keys_are_anonymized(anonymizer, sample_env):
    report = anonymizer.anonymize("prod", sample_env)
    entry = next(e for e in report.entries if e.key == "DB_PASSWORD")
    assert entry.is_sensitive is True
    assert entry.anonymized_value != "supersecret"
    assert len(entry.anonymized_value) == 16  # sha256 hex[:16]


def test_plain_keys_keep_original_value(anonymizer, sample_env):
    report = anonymizer.anonymize("prod", sample_env)
    entry = next(e for e in report.entries if e.key == "APP_NAME")
    assert entry.is_sensitive is False
    assert entry.anonymized_value == "myapp"


def test_mask_method_uses_asterisks(sample_env):
    anon = KeyAnonymizer(method="mask")
    report = anon.anonymize("prod", sample_env)
    entry = next(e for e in report.entries if e.key == "DB_PASSWORD")
    assert set(entry.anonymized_value) == {"*"}


def test_redact_method_uses_label(sample_env):
    anon = KeyAnonymizer(method="redact")
    report = anon.anonymize("prod", sample_env)
    entry = next(e for e in report.entries if e.key == "API_KEY")
    assert entry.anonymized_value == "[REDACTED]"


def test_invalid_method_raises():
    with pytest.raises(ValueError, match="Unknown anonymization method"):
        KeyAnonymizer(method="scramble")


def test_anonymized_env_returns_dict(anonymizer, sample_env):
    report = anonymizer.anonymize("prod", sample_env)
    result = report.anonymized_env()
    assert isinstance(result, dict)
    assert "DB_PASSWORD" in result
    assert result["APP_NAME"] == "myapp"


def test_anonymize_all_handles_multiple_envs(anonymizer, sample_env):
    envs = {"prod": sample_env, "staging": {"APP_NAME": "staging-app", "DB_PASSWORD": "pwd"}}
    reports = anonymizer.anonymize_all(envs)
    assert set(reports.keys()) == {"prod", "staging"}


def test_formatter_format_report_contains_env_name(sample_env):
    anon = KeyAnonymizer(method="redact")
    report = anon.anonymize("prod", sample_env)
    formatter = AnonymizationFormatter(color=False)
    output = formatter.format_report(report)
    assert "prod" in output
    assert "DB_PASSWORD" in output


def test_formatter_summary_counts_sensitive(sample_env):
    anon = KeyAnonymizer(method="redact")
    reports = anon.anonymize_all({"prod": sample_env})
    formatter = AnonymizationFormatter(color=False)
    summary = formatter.format_summary(reports)
    assert "Sensitive keys" in summary
    assert "3" in summary  # DB_PASSWORD, API_KEY, SECRET_TOKEN
