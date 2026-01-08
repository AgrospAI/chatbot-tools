from pathlib import Path

import fastrag

PACKAGE_DIR = Path(fastrag.__file__).parent.parent
RESOURCES_DIR = PACKAGE_DIR / "resources"
DEFAULT_CONFIG = RESOURCES_DIR / "config.yaml"
