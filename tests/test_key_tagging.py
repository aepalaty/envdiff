import pytest
from envdiff.key_tagging import KeyTagger, TagReport, TagEntry
from envdiff.tagging_formatter import TaggingFormatter


@pytest.fixture
def tagger() -> KeyTagger:
    return KeyTagger()


@pytest.fixture
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "JWT_SECRET": "abc123",
        "REDIS_URL": "redis://localhost",
        "APP_NAME": "myapp",
        "S3_BUCKET": "my-bucket",
        "LOG_LEVEL": "info",
    }


def test_calculate_returns_report(tagger, sample_env):
    report = tagger.calculate(sample_env, env_name="staging")
    assert isinstance(report, TagReport)
    assert report.env_name == "staging"


def test_all_keys_collected(tagger, sample_env):
    report = tagger.calculate(sample_env)
    keys = [e.key for e in report.entries]
    assert set(keys) == set(sample_env.keys())


def test_db_keys_tagged_database(tagger, sample_env):
    report = tagger.calculate(sample_env)
    assert "database" in report.tags_for_key("DB_HOST")
    assert "database" in report.tags_for_key("DB_PORT")


def test_jwt_key_tagged_auth(tagger, sample_env):
    report = tagger.calculate(sample_env)
    assert "auth" in report.tags_for_key("JWT_SECRET")


def test_redis_key_tagged_cache(tagger, sample_env):
    report = tagger.calculate(sample_env)
    assert "cache" in report.tags_for_key("REDIS_URL")


def test_s3_key_tagged_storage(tagger, sample_env):
    report = tagger.calculate(sample_env)
    assert "storage" in report.tags_for_key("S3_BUCKET")


def test_log_key_tagged_observability(tagger, sample_env):
    report = tagger.calculate(sample_env)
    assert "observability" in report.tags_for_key("LOG_LEVEL")


def test_untagged_key_captured(tagger, sample_env):
    report = tagger.calculate(sample_env)
    assert "APP_NAME" in report.untagged_keys()


def test_keys_for_tag_returns_correct_list(tagger, sample_env):
    report = tagger.calculate(sample_env)
    db_keys = report.keys_for_tag("database")
    assert "DB_HOST" in db_keys
    assert "DB_PORT" in db_keys


def test_custom_tags_applied(sample_env):
    custom_tagger = KeyTagger(custom_tags={"app": ["APP_"]})
    report = custom_tagger.calculate(sample_env)
    assert "app" in report.tags_for_key("APP_NAME")


def test_all_tags_returns_union(tagger, sample_env):
    report = tagger.calculate(sample_env)
    tags = report.all_tags()
    assert "database" in tags
    assert "auth" in tags
    assert "cache" in tags


def test_formatter_output_includes_tag_headers(sample_env):
    tagger = KeyTagger()
    formatter = TaggingFormatter(color=False)
    report = tagger.calculate(sample_env, env_name="prod")
    output = formatter.format_report(report)
    assert "[database]" in output
    assert "[auth]" in output
    assert "DB_HOST" in output


def test_formatter_shows_untagged(sample_env):
    tagger = KeyTagger()
    formatter = TaggingFormatter(color=False)
    report = tagger.calculate(sample_env)
    output = formatter.format_report(report)
    assert "[untagged]" in output
    assert "APP_NAME" in output


def test_formatter_empty_env():
    tagger = KeyTagger()
    formatter = TaggingFormatter(color=False)
    report = tagger.calculate({})
    output = formatter.format_report(report)
    assert "No keys found" in output
