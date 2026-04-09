"""Parser module for .env files."""

import re
from pathlib import Path
from typing import Dict, Optional


class EnvParser:
    """Parse .env files and extract key-value pairs."""

    # Regex pattern for valid env lines
    # Matches: KEY=value, KEY="value", KEY='value', export KEY=value
    ENV_LINE_PATTERN = re.compile(
        r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$'
    )

    @staticmethod
    def parse_file(file_path: str) -> Dict[str, str]:
        """Parse an .env file and return a dictionary of key-value pairs.
        
        Args:
            file_path: Path to the .env file
            
        Returns:
            Dictionary mapping environment variable names to their values
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If the file cannot be read
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")
        
        env_vars = {}
        
        with open(path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Skip empty lines and comments
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                
                # Try to parse the line
                parsed = EnvParser._parse_line(stripped)
                if parsed:
                    key, value = parsed
                    env_vars[key] = value
        
        return env_vars

    @staticmethod
    def _parse_line(line: str) -> Optional[tuple[str, str]]:
        """Parse a single line from an .env file.
        
        Args:
            line: A single line from the .env file
            
        Returns:
            Tuple of (key, value) or None if line is invalid
        """
        match = EnvParser.ENV_LINE_PATTERN.match(line)
        if not match:
            return None
        
        key = match.group(1)
        value = match.group(2).strip()
        
        # Remove quotes if present
        if len(value) >= 2:
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
        
        return key, value
