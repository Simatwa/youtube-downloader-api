from pathlib import Path

from dotenv import dotenv_values

from app.models import EnvVariables

loaded_config = EnvVariables(**dotenv_values())
"""Loaded from .env file"""

working_dir = Path(loaded_config.working_directory)

download_dir = working_dir / "downloads"

temp_dir = working_dir / "temps"
