from pathlib import Path
from typing import Dict
import os


def load_env(path: str = ".env") -> Dict[str, str]:
    """Load environment variables from a .env file."""
    env_path = Path(path)
    if not env_path.exists():
        return {}
    variables: Dict[str, str] = {}
    for line in env_path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        variables[key] = value
        os.environ.setdefault(key, value)
    return variables
