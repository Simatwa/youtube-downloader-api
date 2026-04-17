"""Global models"""

import logging
import os
from pathlib import Path
from typing import Literal

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    HttpUrl,
    PositiveInt,
    field_validator,
)


class CustomWebsocketResponse(BaseModel):
    status: Literal["downloading", "finished", "completed", "error"]
    detail: dict


class ConfigModel(BaseModel):
    # contacts
    contact_name: str | None = "Unknown"
    contact_email: EmailStr | None = "email@localhost.dev"
    contact_url: HttpUrl | None = "http://localhost:8000/"
    # API
    api_description: str | None = ""
    api_title: str | None = "Youtube-Downloader"
    api_terms_of_service: HttpUrl | None = (
        "http://localhost:8000/terms-of-service"
    )

    visitorData: str | None = Field(
        None, description="Extracted along with po token"
    )
    po_token: str | None = Field(
        None,
        description="How to extract it refer to : https://github.com/yt-dlp/yt-dlp/wiki/Extractors#"
        "manually-acquiring-a-po-token-from-a-browser-for-use-when-logged-out",
    )
    filename_prefix: str | None = ""
    working_directory: str | None = os.getcwd()
    clear_temps: bool | None = True
    search_limit: int | None = 50
    video_info_cache_period_in_hrs: PositiveInt | None = 4
    database_engine: str | None = "sqlite:///db.sqlite3"
    default_extension: Literal["mp4", "webm"] = "webm"
    frontend_dir: str | None = None

    # static server options
    static_server_url: str | None = None

    serve_frontend_from_static_server: bool | None = False

    api_base_url: str | None = None

    # Downloader params - yt_dlp
    default_audio_format: Literal["webm", "m4a"] = "m4a"
    enable_logging: bool | None = False
    proxy: str | None = None
    cookiefile: str | None = None
    http_chunk_size: int | None = 4096
    updatetime: bool | None = False
    buffersize: int | None = None
    ratelimit: int | None = None
    throttledratelimit: int | None = None
    min_filesize: int | None = None
    max_filesize: int | None = None
    noresizebuffer: bool | None = None
    retries: int | None = 2
    continuedl: bool | None = False
    noprogress: bool | None = False
    nopart: bool | None = False
    concurrent_fragment_downloads: int | None = 1
    # YoutubeDL params
    verbose: bool | None = None
    quiet: bool | None = None
    allow_multiple_video_streams: bool | None = None
    allow_multiple_audio_streams: bool | None = None
    geo_bypass: bool | None = True
    geo_bypass_country: str | None = None
    # Post-download opts
    embed_subtitles: bool | None = False

    append_id_in_filename: bool = False

    js_runtime: str | None = None
    js_runtime_name: str | None = "deno"

    clear_downloaded_contents: bool = True

    @property
    def ytdlp_params(self) -> dict[str, int | bool | None]:

        if self.serve_frontend_from_static_server and not self.frontend_dir:
            raise Exception(
                "You have specified to serve frontend contents from static server"
                " yet you have NOT specified the FRONTEND-DIR. "
                "Set the path to frontend_dir in the .env (config) file."
            )

        params = {
            "cookiefile": self.cookiefile,
            # http_chunk_size=self.http_chunk_size, # activating this makes
            # download speed so slow. Consider giving it a fix.
            "updatetime": self.updatetime,
            # buffersize=self.buffersize,
            "ratelimit": self.ratelimit,
            "throttledratelimit": self.throttledratelimit,
            "min_filesize": self.min_filesize,
            "max_filesize": self.max_filesize,
            "noresizebuffer": self.noresizebuffer,
            "retries": self.retries,
            "continuedl": self.continuedl,
            "noprogress": self.noprogress,
            "nopart": self.nopart,
            "concurrent_fragment_downloads": self.concurrent_fragment_downloads,
            "verbose": self.verbose,
            "quiet": self.quiet,
            "allow_multiple_video_streams": self.allow_multiple_video_streams,
            "allow_multiple_audio_streams": self.allow_multiple_audio_streams,
            "geo_bypass": self.geo_bypass,
            "geo_bypass_country": self.geo_bypass_country,
            "keep_fragments": False,
            "fragment_retries": 2,
            # runtimes
        }

        if self.js_runtime:
            params["js_runtimes"] = {
                self.js_runtime_name: {"path": self.js_runtime}
            }

        if self.proxy:
            # Passing proxy with null value makes download to fail
            params["proxy"] = self.proxy

        if self.enable_logging:
            params["logger"] = logging.getLogger("uvicorn")

        if self.quiet:
            # Assumes it's running in production mode
            logging.getLogger("yt_dlp_bonus").setLevel(logging.ERROR)
            logging.getLogger("yt_dlp").setLevel(logging.ERROR)
        if self.po_token:
            if self.cookiefile:
                params["extractor_args"] = {
                    "youtube": {
                        "player_client": ["web", "default"],
                        "po_token": [f"web+{self.po_token}"],
                    }
                }
            elif self.visitorData:
                params["extractor_args"] = {
                    "youtube": {
                        "player_client": ["web", "default"],
                        "player_skip": ["webpage", "configs"],
                        "po_token": [f"web+{self.po_token}"],
                        "visitor_data": [self.visitorData],
                    }
                }
            else:
                raise ValueError(
                    "po_token requires either cookiefile or visitorData."
                )
        elif self.visitorData:
            params["extractor_args"] = {
                "youtube": {
                    "visitor_data": [self.visitorData],
                }
            }

        return params

    @field_validator("api_description")
    def validate_api_description(value):
        if not value:
            return ""
        description_path = Path(value)
        if not description_path.exists() or not description_path.is_file():
            raise ValueError(
                f"Invalid value for api_description passed - {value}."
                " Must be a valid path to a file."
            )
        with open(value) as fh:
            return fh.read()

    @field_validator("working_directory")
    def validate_working_directory(value):
        working_dir = Path(value)
        if value == "static" and not working_dir.exists():
            os.mkdir("static")

        elif not working_dir.exists() or not working_dir.is_dir():
            raise ValueError(f"Invalid working_directory passed - {value}")
        return value

    @field_validator("cookiefile")
    def validate_cookiefile(value):
        if not value:
            return
        cookiefile = Path(value)
        if not cookiefile.exists() or not cookiefile.is_file():
            raise ValueError(f"Invalid cookiefile passed - {value}")
        return value

    @field_validator("js_runtime")
    def validate_js_runtimes(value):
        if not value:
            return
        file = Path(value)
        if not file.exists() or not file.is_file():
            raise ValueError(f"Invalid value for js_runtime passed - {value}")
        return value

    @field_validator("frontend_dir")
    def validate_frontend_dir(value):
        if not value:
            return
        frontend_dir = Path(value)
        if not frontend_dir.exists() or not frontend_dir.is_dir():
            raise ValueError(f"Invalid frontend_dir passed - {value}")

        if not frontend_dir.joinpath("index.html").exists():
            raise ValueError(
                f"Frontend-dir must contain index.html file - {value}"
            )
        return value

    @field_validator("static_server_url")
    def validate_static_server_url(value: str | None):
        if value and not value.startswith("http"):
            raise ValueError(f"Invalid value for static_server_url - {value}")

        return value

    @field_validator("filename_prefix")
    def validate_filename_prefix(value):
        if not value:
            return ""
        return value + " "

    def po_token_verifier(self) -> tuple[str, str]:
        return self.visitorData, self.po_token

    @property
    def contacts(self) -> dict[str, str | EmailStr]:
        """API' contact details"""
        return {
            "name": self.contact_name,
            "email": str(self.contact_email),
            "url": str(self.contact_url),
        }

    @property
    def api_base_url_validated(self) -> str:
        """Checks that `api_base_url` is not None"""
        if not self.api_base_url:
            raise ValueError("Base url for API cannot be null.")

        return self.api_base_url
