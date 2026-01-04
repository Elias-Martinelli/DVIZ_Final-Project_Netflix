"""Central env-management for the project
 This file is responsible for loading environment variables and setting up configurations
"""
from pathlib import Path


def find_project_root() -> Path:
    """Walks up to find config.py which lies 1 leel below the root.
    """
    marker = "src/config.py" # .env funktioniert nicht in Docker
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / marker).exists():
            return parent
    raise RuntimeError("Projekt-Root not found!")

### CONSTANT SETTINGS (not available in .env)
PROJECT_ROOT = find_project_root()
DATA_DIR = PROJECT_ROOT / "data/"
