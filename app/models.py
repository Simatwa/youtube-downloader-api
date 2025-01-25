"""Global models"""

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    PositiveInt,
    EmailStr,
    HttpUrl,
)
from typing import Optional, Literal
from pathlib import Path
import os
import logging


class CustomWebsocketResponse(BaseModel):
    status: Literal["downloading", "finished", "completed", "error"]
    detail: dict


class EnvVariables(BaseModel):
    # contacts
    contact_name: Optional[str] = "Unknown"
    contact_email: Optional[EmailStr] = "email@localhost.dev"
    contact_url: Optional[HttpUrl] = "http://localhost:8000/"
    # API
    api_description: Optional[str] = ""
    api_title: Optional[str] = "Youtube-Downloader"
    api_description: Optional[str] = ""
    api_terms_of_service: Optional[HttpUrl] = "http://localhost:8000/terms-of-service"

    visitorData: Optional[str] = Field(
        None, description="Extracted along with po token"
    )
    po_token: Optional[str] = Field(
        None,
        description="How to extract it refer to : https://github.com/yt-dlp/yt-dlp/wiki/Extractors#"
        "manually-acquiring-a-po-token-from-a-browser-for-use-when-logged-out",
    )
    filename_prefix: Optional[str] = ""
    working_directory: Optional[str] = os.getcwd()
    clear_temps: Optional[bool] = True
    search_limit: Optional[int] = 50
    video_info_cache_period_in_hrs: Optional[PositiveInt] = 4
    database_engine: Optional[str] = "sqlite:///db.sqlite3"
    default_extension: Literal["mp4", "webm"] = "webm"
    frontend_dir: Optional[str] = None

    # static server options
    static_server_url: Optional[str] = None

    serve_frontend_from_static_server: Optional[bool] = False

    api_base_url: Optional[str] = None

    # Downloader params - yt_dlp
    default_audio_format: Literal["webm", "m4a"] = "m4a"
    enable_logging: Optional[bool] = False
    proxy: Optional[str] = None
    cookiefile: Optional[str] = None
    http_chunk_size: Optional[int] = 4096
    updatetime: Optional[bool] = False
    buffersize: Optional[int] = None
    ratelimit: Optional[int] = None
    throttledratelimit: Optional[int] = None
    min_filesize: Optional[int] = None
    max_filesize: Optional[int] = None
    noresizebuffer: Optional[bool] = None
    retries: Optional[int] = 2
    continuedl: Optional[bool] = False
    noprogress: Optional[bool] = False
    nopart: Optional[bool] = False
    concurrent_fragment_downloads: Optional[int] = 1
    # YoutubeDL params
    verbose: Optional[bool] = None
    quiet: Optional[bool] = None
    allow_multiple_video_streams: Optional[bool] = None
    allow_multiple_audio_streams: Optional[bool] = None
    geo_bypass: Optional[bool] = True
    geo_bypass_country: Optional[str] = None
    # Post-download opts
    embed_subtitles: Optional[bool] = False

    append_id_in_filename: bool = False

    @property
    def ytdlp_params(self) -> dict[str, int | bool | None]:

        if self.serve_frontend_from_static_server and not self.frontend_dir:
            raise Exception(
                "You have specified to serve frontend contents from static server "
                "yet you have NOT specified the FRONTEND-DIR. "
                "Set the path to frontend_dir in the .env (config) file."
            )
        params = dict(
            cookiefile=self.cookiefile,
            # http_chunk_size=self.http_chunk_size, # activating this makes
            # download speed so slow. Consider giving it a fix.
            updatetime=self.updatetime,
            # buffersize=self.buffersize,
            ratelimit=self.ratelimit,
            throttledratelimit=self.throttledratelimit,
            min_filesize=self.min_filesize,
            max_filesize=self.max_filesize,
            noresizebuffer=self.noresizebuffer,
            retries=self.retries,
            continuedl=self.continuedl,
            noprogress=self.noprogress,
            nopart=self.nopart,
            concurrent_fragment_downloads=self.concurrent_fragment_downloads,
            verbose=self.verbose,
            quiet=self.quiet,
            allow_multiple_video_streams=self.allow_multiple_video_streams,
            allow_multiple_audio_streams=self.allow_multiple_audio_streams,
            geo_bypass=self.geo_bypass,
            geo_bypass_country=self.geo_bypass_country,
            keep_fragments=False,
            fragment_retries=2,
        )
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
                raise ValueError(f"po_token requires either cookiefile or visitorData.")
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
            raise TypeError(
                f"Invalid value for api_description passed - {value}. Must be a valid path to a file."
            )
        with open(value) as fh:
            return fh.read()

    @field_validator("working_directory")
    def validate_working_directory(value):
        working_dir = Path(value)
        if value == "static" and not working_dir.exists():
            os.mkdir("static")
        elif not working_dir.exists() or not working_dir.is_dir():
            raise TypeError(f"Invalid working_directory passed - {value}")
        return value

    @field_validator("cookiefile")
    def validate_cookiefile(value):
        if not value:
            return
        cookiefile = Path(value)
        if not cookiefile.exists() or not cookiefile.is_file():
            raise TypeError(f"Invalid cookiefile passed - {value}")
        return value

    @field_validator("frontend_dir")
    def validate_frontend_dir(value):
        if not value:
            return
        frontend_dir = Path(value)
        if not frontend_dir.exists() or not frontend_dir.is_dir():
            raise TypeError(f"Invalid frontend_dir passed - {value}")
        if not frontend_dir.joinpath("index.html").exists():
            raise TypeError(f"Frontend-dir must contain index.html file - {value}")
        return value

    @field_validator("static_server_url")
    def validate_static_server_url(value: str | None):
        if value and not value.startswith("http"):
            raise TypeError(f"Invalid value for static_server_url - {value}")
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
        return dict(
            name=self.contact_name,
            email=str(self.contact_email),
            url=str(self.contact_url),
        )

    @property
    def api_base_url_validated(self) -> str:
        """Checks that `api_base_url` is not None"""
        if not self.api_base_url:
            raise ValueError("Base url for API cannot be null.")
        return self.api_base_url
