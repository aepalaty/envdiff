"""Tests for envdiff package."""

import os
import tempfile
from pathlib import Path


def create_temp_env_file(contents: str) -> Path:
    """Create a temporary .env file with the given contents for testing.

    Args:
        contents: The string contents to write to the temp file.

    Returns:
        Path to the created temporary file.
    """
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".env", delete=False
    )
    tmp.write(contents)
    tmp.close()
    return Path(tmp.name)
