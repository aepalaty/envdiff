import pytest
from envdiff.key_heatmap import HeatmapCalculator, HeatmapReport, HeatmapCell


@pytest.fixture
def calculator():
    return HeatmapCalculator()


@pytest.fixture
def three_envs():
    return {
        "dev": {"DB_URL": "postgres://dev", "SECRET_KEY": "devkey", "DEBUG": "true"},
        "staging": {"DB_URL": "postgres://staging", "SECRET_KEY": "stagingkey"},
        "prod": {"DB_URL": "postgres://prod", "API_TOKEN": "prodtoken"},
    }


def test_calculate_returns_report(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert isinstance(report, HeatmapReport)


def test_all_keys_collected(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.keys) == {"API_TOKEN", "DB_URL", "DEBUG", "SECRET_KEY"}


def test_env_names_captured(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_present_key_marked_correctly(calculator, three_envs):
    report = calculator.calculate(three_envs)
    cell = report.cells[("dev", "DB_URL")]
    assert cell.present is True
    assert cell.value == "postgres://dev"


def test_missing_key_marked_correctly(calculator, three_envs):
    report = calculator.calculate(three_envs)
    cell = report.cells[("prod", "DEBUG")]
    assert cell.present is False
    assert cell.value == ""


def test_sensitive_key_flagged(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert report.cells[("dev", "SECRET_KEY")].is_sensitive is True
    assert report.cells[("prod", "API_TOKEN")].is_sensitive is True


def test_non_sensitive_key_not_flagged(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert report.cells[("dev", "DEBUG")].is_sensitive is False


def test_coverage_for_key_universal(calculator, three_envs):
    report = calculator.calculate(three_envs)
    assert report.coverage_for_key("DB_URL") == pytest.approx(1.0)


def test_coverage_for_key_partial(calculator, three_envs):
    report = calculator.calculate(three_envs)
    # SECRET_KEY present in dev and staging only
    assert report.coverage_for_key("SECRET_KEY") == pytest.approx(2 / 3)


def test_coverage_for_env_full(calculator, three_envs):
    report = calculator.calculate(three_envs)
    # dev has DB_URL, SECRET_KEY, DEBUG — missing API_TOKEN
    assert report.coverage_for_env("dev") == pytest.approx(3 / 4)


def test_missing_in_env(calculator, three_envs):
    report = calculator.calculate(three_envs)
    missing = report.missing_in_env("prod")
    assert "DEBUG" in missing
    assert "SECRET_KEY" in missing
    assert "DB_URL" not in missing


def test_heatmap_cell_str(calculator, three_envs):
    report = calculator.calculate(three_envs)
    cell = report.cells[("dev", "DB_URL")]
    assert "dev/DB_URL" in str(cell)
    assert "present" in str(cell)


def test_empty_envs_returns_empty_report(calculator):
    report = calculator.calculate({})
    assert report.keys == []
    assert report.env_names == []
    assert report.cells == {}
