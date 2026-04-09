"""Tests for envdiff.redact_config."""

import json
import pytest
from pathlib import Path

from envdiff.redact_config import load_redact_config
from envdiff.redactor import DEFAULT_MASK


@pytest.fixture
def json_config(tmp_path: Path) -> Path:
    cfg = {
        "sensitive_keys": ["MY_SUPER_SECRET"],
        "mask": "[HIDDEN]",
        "auto_detect": False,
    }
    p = tmp_path / ".envdiff-redact.json"
    p.write_text(json.dumps(cfg))
    return p


def test_load_from_json(json_config):
    r = load_redact_config(json_config)
    assert r.mask == "[HIDDEN]"
    assert r.auto_detect is False
    assert r.is_sensitive("MY_SUPER_SECRET") is True


def test_auto_detect_disabled_via_config(json_config):
    r = load_redact_config(json_config)
    # auto_detect=False so pattern-based detection is off
    assert r.is_sensitive("DB_PASSWORD") is False


def test_no_config_returns_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r = load_redact_config()
    assert r.mask == DEFAULT_MASK
    assert r.auto_detect is True


def test_missing_explicit_path_raises(tmp_path):
    missing = tmp_path / "nonexistent.json"
    with pytest.raises(FileNotFoundError):
        load_redact_config(missing)


def test_auto_discover_json(tmp_path, monkeypatch):
    cfg = {"sensitive_keys": ["DISCOVERED_KEY"], "auto_detect": False}
    (tmp_path / ".envdiff-redact.json").write_text(json.dumps(cfg))
    monkeypatch.chdir(tmp_path)
    r = load_redact_config()
    assert r.is_sensitive("DISCOVERED_KEY") is True
