"""Tests for TemplateGenerator and EnvTemplate."""

import pytest

from envdiff.env_template import EnvTemplate, TemplateEntry, TemplateGenerator
from envdiff.redactor import Redactor


@pytest.fixture
def generator() -> TemplateGenerator:
    return TemplateGenerator()


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DATABASE_URL": "postgres://localhost/db",
        "SECRET_KEY": "supersecret",
        "API_TOKEN": "tok_abc123",
        "DEBUG": "true",
    }


def test_non_sensitive_key_keeps_value(generator, sample_env):
    template = generator.generate({"APP_NAME": "myapp"})
    assert template.entries[0].placeholder == "myapp"


def test_sensitive_key_replaced_with_placeholder(generator, sample_env):
    template = generator.generate({"SECRET_KEY": "supersecret"})
    assert template.entries[0].placeholder == "CHANGE_ME"


def test_sensitive_key_has_comment(generator):
    template = generator.generate({"API_TOKEN": "tok_abc"})
    assert template.entries[0].comment is not None
    assert "sensitive" in template.entries[0].comment


def test_custom_placeholder():
    gen = TemplateGenerator(placeholder="<FILL_IN>")
    template = gen.generate({"PASSWORD": "secret"})
    assert template.entries[0].placeholder == "<FILL_IN>"


def test_required_keys_marked_correctly():
    gen = TemplateGenerator(required_keys=["APP_NAME"])
    template = gen.generate({"APP_NAME": "x", "DEBUG": "true"})
    by_key = {e.key: e for e in template.entries}
    assert by_key["APP_NAME"].required is True
    assert by_key["DEBUG"].required is False


def test_all_keys_required_when_none_specified(generator, sample_env):
    template = generator.generate(sample_env)
    assert all(e.required for e in template.entries)


def test_entries_sorted_alphabetically(generator, sample_env):
    template = generator.generate(sample_env)
    keys = [e.key for e in template.entries]
    assert keys == sorted(keys)


def test_render_produces_non_empty_string(generator, sample_env):
    template = generator.generate(sample_env)
    rendered = template.render()
    assert "APP_NAME" in rendered
    assert "SECRET_KEY" in rendered


def test_template_entry_render_with_comment():
    entry = TemplateEntry(key="DB_PASS", placeholder="CHANGE_ME", comment="keep secret")
    rendered = entry.render()
    assert rendered.startswith("# keep secret")
    assert "DB_PASS=CHANGE_ME" in rendered


def test_template_entry_render_optional_marker():
    entry = TemplateEntry(key="DEBUG", placeholder="false", required=False)
    rendered = entry.render()
    assert "optional" in rendered
