import pytest
from envdiff.key_search import KeySearcher, SearchResult, SearchMatch


ENV_A = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "abc123",
    "APP_DEBUG": "true",
}

ENV_B = {
    "DATABASE_URL": "mysql://remote/db",
    "APP_PORT": "8080",
    "API_TOKEN": "xyz789",
}

ENVS = {"staging": ENV_A, "production": ENV_B}


@pytest.fixture
def searcher():
    return KeySearcher(search_keys=True, search_values=False)


def test_search_key_substring_match(searcher):
    result = searcher.search(ENVS, "DATABASE")
    assert result.has_matches
    assert "DATABASE_URL" in result.matched_keys


def test_search_returns_all_envs_with_key(searcher):
    result = searcher.search(ENVS, "DATABASE_URL")
    assert set(result.matched_envs) == {"staging", "production"}


def test_search_no_match_returns_empty(searcher):
    result = searcher.search(ENVS, "NONEXISTENT_KEY")
    assert not result.has_matches
    assert result.matches == []


def test_search_case_insensitive(searcher):
    result = searcher.search(ENVS, "app")
    keys = result.matched_keys
    assert "APP_DEBUG" in keys or "APP_PORT" in keys


def test_search_value_disabled_by_default(searcher):
    result = searcher.search(ENVS, "abc123")
    assert not result.has_matches


def test_search_value_enabled():
    s = KeySearcher(search_keys=False, search_values=True)
    result = s.search(ENVS, "abc123")
    assert result.has_matches
    assert result.matches[0].matched_by == "value"


def test_search_both_keys_and_values():
    s = KeySearcher(search_keys=True, search_values=True)
    # 'db' matches DATABASE_URL key and 'postgres://localhost/db' value
    result = s.search({"env": {"DATABASE_URL": "postgres://localhost/db"}}, "db")
    assert result.has_matches
    match = result.matches[0]
    assert match.matched_by == "both"


def test_glob_pattern_match(searcher):
    result = searcher.search(ENVS, "APP_*", glob=True)
    assert result.has_matches
    for m in result.matches:
        assert m.key.startswith("APP_")


def test_glob_no_match(searcher):
    result = searcher.search(ENVS, "MISSING_*", glob=True)
    assert not result.has_matches


def test_matched_keys_are_unique(searcher):
    result = searcher.search(ENVS, "DATABASE_URL")
    assert len(result.matched_keys) == 1
    assert result.matched_keys == ["DATABASE_URL"]


def test_search_match_str():
    match = SearchMatch(key="FOO", env_name="dev", value="bar", matched_by="key")
    assert "FOO" in str(match)
    assert "dev" in str(match)
    assert "key" in str(match)
