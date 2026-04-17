import tomllib
from pathlib import Path

from dotenv import dotenv_values

from app.models import EnvVariables

loaded_config = EnvVariables(**dotenv_values())
"""Loaded from .env file"""

WORKING_DIR = Path(loaded_config.working_directory)

PROJECT_DIR = Path(__file__).parent.parent

DOWNLOAD_DIR = WORKING_DIR / "downloads"

TEMP_DIR = WORKING_DIR / "temps"


PYPROJECT_DOT_TOML_PATH = PROJECT_DIR / "pyproject.toml"

pyproject_dot_toml_details = tomllib.load(open(PYPROJECT_DOT_TOML_PATH, "rb"))
