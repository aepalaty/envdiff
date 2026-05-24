import pytest
from envdiff.key_compression import CompressionCalculator, CompressionReport
from envdiff.compression_formatter import CompressionFormatter


@pytest.fixture
def calculator():
    return CompressionCalculator()


@pytest.fixture
def three_envs():
    return {
        "dev": {
            "DB_URL": "postgres://localhost:5432/dev",
            "APP_NAME": "myapp",
            "SECRET_KEY": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        },
        "staging": {
            "DB_URL": "postgres://staging-host:5432/staging",
            "APP_NAME": "myapp",
            "SECRET_KEY": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        },
        "prod": {
            "DB_URL": "postgres://prod-host:5432/prod",
            "APP_NAME": "myapp",
            "SECRET_KEY": "s3cR3t!v@lueW1thL0tsOfV4r1ety!XyZ#123",
        },
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, CompressionReport)


def test_env_names_captured(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_all_keys_collected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    keys = {e.key for e in report.entries}
    assert keys == {"DB_URL", "APP_NAME", "SECRET_KEY"}


def test_repeated_chars_have_low_ratio(calculator):
    envs = {"env": {"KEY": "a" * 64}}
    report = calculator.calculate(envs)
    entry = report.entry_for_key("KEY")
    assert entry is not None
    assert entry.ratio < 0.5


def test_high_variety_value_has_high_ratio(calculator):
    envs = {"env": {"KEY": "aB3$xZ9!qW2@mN7#"}}
    report = calculator.calculate(envs)
    entry = report.entry_for_key("KEY")
    assert entry is not None
    assert entry.ratio > 0.5


def test_empty_value_does_not_crash(calculator):
    envs = {"env": {"EMPTY": ""}}
    report = calculator.calculate(envs)
    entry = report.entry_for_key("EMPTY")
    assert entry is not None
    assert entry.compressed_size == 0


def test_compressible_keys_filters_correctly(calculator, three_envs):
    report = calculator.calculate(three_envs)
    for entry in report.compressible_keys:
        assert entry.is_compressible


def test_average_ratio_between_zero_and_one(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert 0.0 <= report.average_ratio <= 1.0


def test_entry_for_key_returns_none_for_missing(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert report.entry_for_key("NONEXISTENT") is None


def test_formatter_renders_without_error(calculator, three_envs):
    report = calculator.calculate(three_envs)
    formatter = CompressionFormatter(color=False)
    output = formatter.format_report(report)
    assert "Key Compression Analysis" in output
    assert "DB_URL" in output


def test_formatter_top_n_limits_output(calculator, three_envs):
    report = calculator.calculate(three_envs)
    formatter = CompressionFormatter(color=False)
    output = formatter.format_report(report, top_n=1)
    # Only one key row should appear in the data section
    key_lines = [l for l in output.splitlines() if "postgres" in l or "myapp" in l or "secret" in l.lower()]
    assert len(key_lines) <= 1
