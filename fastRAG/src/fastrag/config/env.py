"""Environment variable loader for .env file support"""

import os
from pathlib import Path


def load_env_file(env_path: Path | None = None) -> None:
    """Load environment variables from a .env file.

    Args:
        env_path: Path to the .env file. If None, searches for .env in common locations.
    """
    if env_path is None:
        # Look for .env in the project root (parent of src directory)
        current_dir = Path.cwd()
        env_path = current_dir / ".env"

        # If not found in current directory, check parent directories
        if not env_path.exists():
            for parent in current_dir.parents:
                potential_env = parent / ".env"
                if potential_env.exists():
                    env_path = potential_env
                    break

    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse KEY=VALUE pairs
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Set environment variable only if not already set
                    if key and key not in os.environ:
                        os.environ[key] = value
