import pytest
from envdiff.key_visibility import VisibilityCalculator, VisibilityReport, _classify
from envdiff.visibility_formatter import VisibilityFormatter


@pytest.fixture
def calculator():
    return VisibilityCalculator()


@pytest.fixture
def three_envs():
    return {
        "dev": {
            "DB_PASSWORD": "devpass",
            "DEBUG_MODE": "true",
            "APP_NAME": "myapp",
        },
        "staging": {
            "DB_PASSWORD": "stagpass",
            "DEBUG_MODE": "false",
            "APP_NAME": "myapp",
            "API_TOKEN": "tok123",
        },
        "prod": {
            "DB_PASSWORD": "prodpass",
            "APP_NAME": "myapp",
            "API_TOKEN": "tok456",
        },
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, VisibilityReport)


def test_env_names_captured(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_all_keys_collected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    keys = {e.key for e in report.entries}
    assert "DB_PASSWORD" in keys
    assert "DEBUG_MODE" in keys
    assert "APP_NAME" in keys
    assert "API_TOKEN" in keys


def test_classify_password_is_private():
    assert _classify("DB_PASSWORD") == "private"


def test_classify_token_is_private():
    assert _classify("API_TOKEN") == "private"


def test_classify_debug_is_internal():
    assert _classify("DEBUG_MODE") == "internal"


def test_classify_app_name_is_public():
    assert _classify("APP_NAME") == "public"


def test_private_keys_grouped_correctly(calculator, three_envs):
    report = calculator.calculate(three_envs)
    private_keys = {e.key for e in report.private_keys()}
    assert "DB_PASSWORD" in private_keys
    assert "API_TOKEN" in private_keys


def test_internal_keys_grouped_correctly(calculator, three_envs):
    report = calculator.calculate(three_envs)
    internal_keys = {e.key for e in report.internal_keys()}
    assert "DEBUG_MODE" in internal_keys


def test_public_keys_grouped_correctly(calculator, three_envs):
    report = calculator.calculate(three_envs)
    public_keys = {e.key for e in report.public_keys()}
    assert "APP_NAME" in public_keys


def test_has_private_true_when_private_keys_exist(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert report.has_private() is True


def test_has_private_false_when_no_private_keys(calculator):
    envs = {"dev": {"APP_NAME": "myapp", "PORT": "8080"}}
    report = calculator.calculate(envs)
    assert report.has_private() is False


def test_formatter_output_contains_private_section(calculator, three_envs):
    report = calculator.calculate(three_envs)
    formatter = VisibilityFormatter(color=False)
    output = formatter.format_report(report)
    assert "Private" in output
    assert "DB_PASSWORD" in output


def test_formatter_output_contains_summary(calculator, three_envs):
    report = calculator.calculate(three_envs)
    formatter = VisibilityFormatter(color=False)
    output = formatter.format_report(report)
    assert "Total:" in output
    assert "private=" in output
