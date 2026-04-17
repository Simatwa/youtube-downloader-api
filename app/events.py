"""Startup and shutdown events"""

import sys
from datetime import timedelta
from shutil import rmtree

from fastapi import FastAPI
from sqlmodel import Session, delete

from app.config import loaded_config
from app.db import VideoInfo, create_tables, engine
from app.utils import DOWNLOAD_DIR, create_temp_dirs, logger, utc_now


def event_create_tempdirs():
    create_temp_dirs()


def event_create_tables():
    create_tables()


def event_delete_expired_extracted_info():
    time_offset = utc_now() - timedelta(
        hours=loaded_config.video_info_cache_period_in_hrs
    )
    delete_query = delete(VideoInfo).where(VideoInfo.updated_on < time_offset)
    with Session(bind=engine) as session:
        logger.info(f"Deleting expired extracted-infos [< {time_offset}]")

        session.exec(delete_query)
        session.commit()
        return time_offset


def event_clear_previous_downloads():
    if loaded_config.clear_downloaded_contents:
        if DOWNLOAD_DIR.exists():
            print(
                f"CLEARING download DIRECTORY {DOWNLOAD_DIR.absolute()!r} "
                f"{loaded_config.clear_downloaded_contents=}",
                file=sys.stderr,
            )
            rmtree(DOWNLOAD_DIR)

    else:
        print(
            f"NOT CLEARING download DIRECTORY {DOWNLOAD_DIR.absolute()!r}. "
            f"{loaded_config.clear_downloaded_contents=}",
            file=sys.stderr,
        )
