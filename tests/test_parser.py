"""Tests for the EnvParser module."""

import pytest
import tempfile
from pathlib import Path
from envdiff.parser import EnvParser


class TestEnvParser:
    """Test cases for EnvParser class."""

    def test_parse_simple_env_file(self):
        """Test parsing a simple .env file."""
        content = """DATABASE_URL=postgres://localhost/mydb
API_KEY=secret123
DEBUG=true
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(content)
            f.flush()
            
            result = EnvParser.parse_file(f.name)
            
            assert result == {
                'DATABASE_URL': 'postgres://localhost/mydb',
                'API_KEY': 'secret123',
                'DEBUG': 'true'
            }
            
            Path(f.name).unlink()

    def test_parse_with_quotes(self):
        """Test parsing values with quotes."""
        content = """SINGLE='single quoted'
DOUBLE="double quoted"
NO_QUOTES=no quotes
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(content)
            f.flush()
            
            result = EnvParser.parse_file(f.name)
            
            assert result['SINGLE'] == 'single quoted'
            assert result['DOUBLE'] == 'double quoted'
            assert result['NO_QUOTES'] == 'no quotes'
            
            Path(f.name).unlink()

    def test_parse_with_comments_and_empty_lines(self):
        """Test that comments and empty lines are ignored."""
        content = """# This is a comment
VALID_KEY=value1

# Another comment
ANOTHER_KEY=value2
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(content)
            f.flush()
            
            result = EnvParser.parse_file(f.name)
            
            assert len(result) == 2
            assert result['VALID_KEY'] == 'value1'
            assert result['ANOTHER_KEY'] == 'value2'
            
            Path(f.name).unlink()

    def test_parse_with_export(self):
        """Test parsing lines with 'export' prefix."""
        content = """export PATH=/usr/bin
export HOME=/home/user
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(content)
            f.flush()
            
            result = EnvParser.parse_file(f.name)
            
            assert result['PATH'] == '/usr/bin'
            assert result['HOME'] == '/home/user'
            
            Path(f.name).unlink()

    def test_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        with pytest.raises(FileNotFoundError):
            EnvParser.parse_file('/nonexistent/file.env')

    def test_not_a_file(self):
        """Test that ValueError is raised when path is not a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Not a file"):
                EnvParser.parse_file(tmpdir)
