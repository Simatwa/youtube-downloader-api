import tomllib
from pathlib import Path

import yaml

from app.models import ConfigModel

PROJECT_DIR = Path(__file__).parent.parent

CONFIG_FILE_PATH = PROJECT_DIR / "config.yml"

config_values = yaml.safe_load(open(CONFIG_FILE_PATH))

loaded_config = ConfigModel(**config_values)
"""Loaded from .env file"""

WORKING_DIR = Path(loaded_config.working_directory)

DOWNLOAD_DIR = WORKING_DIR / "downloads"

TEMP_DIR = WORKING_DIR / "temps"


PYPROJECT_DOT_TOML_PATH = PROJECT_DIR / "pyproject.toml"

pyproject_dot_toml_details = tomllib.load(open(PYPROJECT_DOT_TOML_PATH, "rb"))
