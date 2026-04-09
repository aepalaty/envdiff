"""Tests for the envdiff CLI module."""

import textwrap
from pathlib import Path

import pytest

from envdiff.cli import run


@pytest.fixture()
def env_baseline(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        APP_ENV=production
        DB_HOST=localhost
        DB_PORT=5432
        SECRET_KEY=abc123
    """)
    p = tmp_path / ".env.baseline"
    p.write_text(content)
    return p


@pytest.fixture()
def env_other(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        APP_ENV=staging
        DB_HOST=localhost
        DB_PORT=5432
    """)
    p = tmp_path / ".env.other"
    p.write_text(content)
    return p


@pytest.fixture()
def env_identical(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        APP_ENV=production
        DB_HOST=localhost
        DB_PORT=5432
        SECRET_KEY=abc123
    """)
    p = tmp_path / ".env.identical"
    p.write_text(content)
    return p


def test_run_requires_at_least_two_files(capsys):
    exit_code = run(["only_one.env"])
    assert exit_code == 2


def test_run_missing_file(tmp_path, capsys):
    existing = tmp_path / ".env"
    existing.write_text("KEY=value\n")
    exit_code = run([str(existing), "nonexistent.env"])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_run_identical_files_returns_zero(env_baseline, env_identical, capsys):
    exit_code = run([str(env_baseline), str(env_identical)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "No differences found" in captured.out


def test_run_with_differences_returns_zero_without_exit_code_flag(
    env_baseline, env_other, capsys
):
    exit_code = run([str(env_baseline), str(env_other)])
    assert exit_code == 0


def test_run_with_differences_returns_one_with_exit_code_flag(
    env_baseline, env_other, capsys
):
    exit_code = run(["--exit-code", str(env_baseline), str(env_other)])
    assert exit_code == 1


def test_run_summary_flag_produces_output(env_baseline, env_other, capsys):
    run(["--summary", str(env_baseline), str(env_other)])
    captured = capsys.readouterr()
    assert captured.out  # summary line should appear


def test_run_no_color_flag_does_not_crash(env_baseline, env_other, capsys):
    exit_code = run(["--no-color", str(env_baseline), str(env_other)])
    assert exit_code in (0, 1)
