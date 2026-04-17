from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl
from yt_dlp_bonus.constants import (
    audioBitratesType,
    audioExtensionsType,
    mediaQualitiesType,
    videoExtensionsType,
)


class SearchVideosResponse(BaseModel):
    class VideoMetadata(BaseModel):
        title: str = Field(description="Video title as in Youtube")
        id: str = Field(description="Video id")
        duration: str | None = Field(None, description="Video's total running")

    query: str = Field(description="Search query")
    results: list[VideoMetadata]

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "diamond songs",
                "results": [
                    {
                        "title": "Rihanna - Diamonds",
                        "id": "0-p5EbAsxUM",
                        "duration": "3:46",
                    },
                    {
                        "title": "Jux Ft Diamond Platnumz - Ololufe Mi "
                        "(Official Video)",
                        "id": "6Z5CEE25QH8",
                        "duration": "4:20",
                    },
                    {
                        "title": "Rihanna - Diamonds",
                        "id": "lWA2pjMjpBs",
                        "duration": "4:43",
                    },
                    {
                        "title": "Diamond | Official Music Video | Gurnam Bhullar"
                        " | Songs 2018 | Jass Records",
                        "id": "ggJMQHltiQc",
                        "duration": "4:21",
                    },
                    {
                        "title": "Diamond Platnumz - Jeje (Official Music Video)",
                        "id": "g5rFro4XdZ0",
                        "duration": "3:19",
                    },
                    {
                        "title": "Diamond Platnumz Ft Mr. Blue & Jay Melody - "
                        "Mapoz (Official Music Video)",
                        "id": "M1dUTxVXS5Q",
                        "duration": "4:08",
                    },
                    {
                        "title": "Diamond Platnumz x Jason Derulo ft Khalil "
                        "Harisson & Chley - Komasava Remix "
                        "(Official Music Video)",
                        "id": "RpZRtX2mQdc",
                        "duration": "4:51",
                    },
                    {
                        "title": "Diamond Platnumz feat Chley - Shu! "
                        "(Official Music Video)",
                        "id": "e2byDgJ8AyA",
                        "duration": "4:25",
                    },
                    {
                        "title": "Diamond platnumz ft Willy Paul _ Yaishe "
                        "(official music video)",
                        "id": "SISK-4gqgc0",
                        "duration": "2:02",
                    },
                    {
                        "title": "1 Hour Diamond Hall Meditation Silent Music "
                        "| #silentmusic #pandavbhawan @BrahmaKumarisHapur",
                        "id": "Fvu0Yn4Yg98",
                        "duration": "1:00:58",
                    },
                ],
            }
        }
    }


class VideoMetadataResponse(BaseModel):
    class MediaMetadata(BaseModel):
        quality: str  # mediaQualitiesType
        size: str | None = None

    class MediaFormats(BaseModel):
        audio: audioExtensionsType
        video: videoExtensionsType

    class OtherMetadata(BaseModel):
        like_count: int | None = None
        views_count: int | None = None
        categories: list[str]
        tags: list[str]

    id: str
    title: str
    channel: str | None = None
    uploader_url: str | None = None
    duration_string: str | None = None
    thumbnail: HttpUrl
    audio: list[MediaMetadata]
    video: list[MediaMetadata]
    format: MediaFormats
    others: OtherMetadata

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "lw5tB9LQQVM",
                "title": "Marioo feat Fathermoh, Sean Mmg, Ssaru & Motif - Statue"
                " (Official Music Video)",
                "channel": "MariooOfficial",
                "uploader_url": "https://www.youtube.com/@MariooOfficialMusic",
                "duration_string": "2:34",
                "thumbnail": "https://i.ytimg.com/vi/lw5tB9LQQVM/sddefault.jpg",
                "audio": [
                    {"quality": "ultralow", "size": "682.92 KB"},
                    {"quality": "low", "size": "1.32 MB"},
                    {"quality": "medium", "size": "2.6 MB"},
                ],
                "video": [
                    {"quality": "144p", "size": "4.14 MB"},
                    {"quality": "240p", "size": "5.99 MB"},
                    {"quality": "360p", "size": "10.43 MB"},
                    {"quality": "480p", "size": "14.88 MB"},
                    {"quality": "720p", "size": "31.64 MB"},
                    {"quality": "1080p", "size": "52.14 MB"},
                    {"quality": "1440p", "size": "171.99 MB"},
                    {"quality": "2160p", "size": "342.56 MB"},
                ],
                "format": {"audio": "m4a", "video": "mp4"},
            }
        }
    }


class MediaDownloadProcessPayload(BaseModel):
    url: str = Field(description="Link to the Youtube video or video id")
    quality: mediaQualitiesType | Literal["bestaudio", "bestvideo", "best"]
    bitrate: audioBitratesType | None = None
    x_lang: str | None = "en"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "url": "https://youtu.be/1-xGerv5FOk?si=Vv_FeKPF_6eDp5di",
                    "quality": "720p",
                    "bitrate": "128k",
                    "x_lang": "en",
                },
                {
                    "url": "1-xGerv5FOk",
                    "quality": "1080p",
                    "bitrate": None,
                },
                {
                    "url": "https://youtu.be/1-xGerv5FOk?si=Vv_FeKPF_6eDp5di",
                    "quality": "medium",
                    "bitrate": "192k",
                },
            ],
        }
    }


class MediaDownloadResponse(BaseModel):
    is_success: bool = Field(description="Download successful status")
    filename: str | None = None
    filesize: str
    link: str | None = Field(
        description="Link pointing to downloadable media file or video id"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "is_success": True,
                "filename": "Alan Walker - Alone 1080p.mp4",
                "filesize": "35.37 MB",
                "link": "//localhost:8000/static/file/Alan%20Walker%20-"
                "%20Alone%201080p.mp4",
            }
        }
    }
