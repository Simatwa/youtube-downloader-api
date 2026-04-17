import asyncio
import json
import typing as t
from functools import lru_cache
from os import path
from pathlib import Path

from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Query,
    Request,
    WebSocket,
    status,
)
from httpx import Proxy
from innertube import InnerTube
from pydantic import ValidationError
from starlette.websockets import WebSocketState
from yt_dlp_bonus import Downloader, YoutubeDLBonus
from yt_dlp_bonus.constants import audioQualities, videoQualities
from yt_dlp_bonus.utils import get_size_string

import app.v1.models as models
from app.config import DOWNLOAD_DIR, TEMP_DIR, loaded_config
from app.models import CustomWebsocketResponse
from app.utils import (
    get_absolute_link_to_static_file,
    logger,
    router_exception_handler,
    sanitize_filename,
    silence_websocket_exceptions,
)
from app.v1.utils import get_extracted_info

router = APIRouter(prefix="/v1")

yt_params = loaded_config.ytdlp_params

yt_params.update({
    "paths": {"home": DOWNLOAD_DIR.as_posix(), "temp": TEMP_DIR.name}
})

yt = YoutubeDLBonus(params=yt_params)

downloader = Downloader(
    yt=yt,
    working_directory=DOWNLOAD_DIR,
    clear_temps=loaded_config.clear_temps,
    filename_prefix=loaded_config.filename_prefix,
)


PARAMS_TYPE_VIDEO = "EgIQAQ%3D%3D"

innertube_client = InnerTube(
    "WEB",
    "2.20230920.00.00",
    # proxies=None if not loaded_config.proxy else Proxy(loaded_config.proxy),
)


@lru_cache(maxsize=100)
def search_videos_by_key(query: str, limit: int = -1) -> list[dict[str, str]]:
    """Perform a video search.

    Args:
        query (str): Search keyword
        limit (int): Total results not to exceed. Defaults to -1 (No limit).

    Returns:
        list[dict[str, str]]: Sorted shallow results.
    """
    video_search_results = innertube_client.search(
        query, params=PARAMS_TYPE_VIDEO
    )
    video_metadata_container: list[dict] = []
    contents = video_search_results["contents"]["twoColumnSearchResultsRenderer"][
        "primaryContents"
    ]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]
    count = 0
    for content in contents:
        try:
            video = content["videoRenderer"]
            video_id = video["videoId"]
            video_title = video["title"]["runs"][0]["text"]
            video_duration = video["lengthText"]["simpleText"]
            video_metadata_container.append(
                dict(id=video_id, title=video_title, duration=video_duration)
            )
            count += 1
            if count == limit:
                break

        except Exception:  # KeyError etc
            pass
    return video_metadata_container


@router.get("/search", name="Search videos")
@router_exception_handler
def search_videos(
    q: str = Query(description="Video title or keyword"),
    limit: int = Query(
        10,
        gt=0,
        le=loaded_config.search_limit,
        description="Videos amount not to exceed.",
    ),
) -> models.SearchVideosResponse:
    """Search videos
    - Search videos matching the query and return whole results at once.
    - Serves from cache similar `99` subsequent queries.
    """
    videos_found = search_videos_by_key(query=q, limit=limit)
    if not videos_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No video matched that query - {q}!",
        )
    return models.SearchVideosResponse(query=q, results=videos_found)


@router.get("/metadata", name="Video metadata")
@router_exception_handler
def get_video_metadata(
    url: str = Query(description="Video URL or ID"),
) -> models.VideoMetadataResponse:
    """Get metadata of a specific video.
    - Similar subsequent requests will be faster as they will be served
    from the cache for a few hours.
    """
    extracted_info = get_extracted_info(yt=yt, url=url)
    video_formats = yt.get_video_qualities_with_extension(
        extracted_info,
        ext=loaded_config.default_extension,
        audio_ext=loaded_config.default_audio_format,
    )
    updated_video_formats = yt.update_audio_video_size(video_formats)
    audio_formats = []
    video_formats = []
    for quality, format in updated_video_formats.items():
        if quality in audioQualities:
            audio_formats.append(
                dict(
                    quality=quality,
                    size=get_size_string(format.audio_video_size),
                )
            )
        else:
            video_formats.append(
                dict(
                    quality=quality,
                    size=get_size_string(format.audio_video_size),
                )
            )

    return models.VideoMetadataResponse(
        id=extracted_info.id,
        title=extracted_info.title,
        channel=extracted_info.channel,
        uploader_url=extracted_info.uploader_url,
        duration_string=extracted_info.duration_string,
        thumbnail=extracted_info.thumbnail,
        audio=audio_formats or [{"quality": "bestaudio"}],
        video=video_formats or [{"quality": "best"}],
        format=dict(
            audio=loaded_config.default_audio_format,
            video="mp4",
        ),
        others=dict(
            like_count=extracted_info.like_count,
            views_count=extracted_info.view_count,
            categories=extracted_info.categories or [],
            tags=extracted_info.tags or [],
        ),
    )


@router.post("/download", name="Process download")
def process_video_for_download(
    request: Request,
    payload: models.MediaDownloadProcessPayload,
    x_lang: t.Annotated[
        str,
        Header(
            description="Two-letter ISO set language code for subtitle purposes."
        ),
    ] = None,
) -> models.MediaDownloadResponse:
    """Initiate download processing
    - To download the media file: Add parameter `download` with value
    `true` to the returned link i.e `?download=true`.
    - Accomplish the same using websocket endpoint at `/api/v1/download/ws`
    """
    payload.x_lang = x_lang or payload.x_lang
    return real_download_process(request, payload)


@router_exception_handler
def real_download_process(
    request: Request | WebSocket,
    payload: models.MediaDownloadProcessPayload,
    progress_hooks: list[t.Callable] = [],
    **kwargs,
) -> models.MediaDownloadResponse:
    extracted_info = get_extracted_info(yt=yt, url=payload.url)
    video_formats = yt.get_video_qualities_with_extension(
        extracted_info,
        ext=loaded_config.default_extension,
        audio_ext=(
            loaded_config.default_audio_format
            if payload.quality in audioQualities
            else "webm"
        ),
    )
    target_format = video_formats.get(payload.quality)
    id_placeholder = ", %(id)s" if loaded_config.append_id_in_filename else ""

    ytdl_opts = {
        "outtmpl": (
            f"{loaded_config.filename_prefix or ''}"
            f"{sanitize_filename(extracted_info.title)} "
            f"(%(format_note)s{id_placeholder}).%(ext)s"
        )
    }

    if loaded_config.embed_subtitles and payload.x_lang is not None:
        ytdl_opts.update({
            "postprocessors": [
                {"already_have_subtitle": False, "key": "FFmpegEmbedSubtitle"}
            ],
            "writeautomaticsub": True,
            "writesubtitles": True,
            "subtitleslangs": [payload.x_lang],
        })

    kwargs["ytdl_params"] = ytdl_opts

    if payload.quality in audioQualities:
        assert target_format, (
            f"The video does not support the audio quality '{payload.quality}'. "
            "Try other audio qualities like "
            f"{
                ', '.join([
                    quality
                    for quality in audioQualities
                    if quality != payload.quality
                ])
            }."
        )
        processed_info_dict = downloader.ydl_run_audio(
            extracted_info,
            audio_format=target_format.format_id,
            bitrate=payload.bitrate,
            progress_hooks=progress_hooks,
            **kwargs,
        )
    elif payload.quality in videoQualities:
        assert target_format, (
            f"The video does not support the video quality '{payload.quality}'. "
            f"Try other video qualities like {
                ', '.join([
                    quality
                    for quality in videoQualities
                    if quality != payload.quality
                ])
            }."
        )
        processed_info_dict = downloader.ydl_run_video(
            extracted_info,
            video_format=target_format.format_id,
            output_ext="mp4",
            progress_hooks=progress_hooks,
            **kwargs,
        )
        # TODO: Consider audio_format as well
    else:
        # bestaudio | bestvideo | best
        if payload.bitrate:
            # audio
            processed_info_dict = downloader.ydl_run_audio(
                extracted_info,
                payload.bitrate,
                audio_format=payload.quality,
            )
        else:
            processed_info_dict = downloader.ydl_run(
                extracted_info,
                video_format=None,
                audio_format=None,
                default_format=payload.quality,
            )

    filepath = Path(processed_info_dict["requested_downloads"][0]["filepath"])

    return models.MediaDownloadResponse(
        is_success=True,
        filename=filepath.name,
        filesize=get_size_string(path.getsize(filepath)),
        link=get_absolute_link_to_static_file(filepath.name, request),
    )


@router.websocket("/download/ws", name="Process download (websocket)")
async def download_websocket_handler(websocket: WebSocket):
    await websocket.accept()

    try:

        async def send_progress(response: CustomWebsocketResponse):
            await websocket.send_json(response.model_dump())

        @silence_websocket_exceptions
        async def close_websocket():
            if websocket.state == WebSocketState.CONNECTED:
                await websocket.close()

        payload_dict: dict = await websocket.receive_json()
        request_payload = models.MediaDownloadProcessPayload(**payload_dict)

        def progress_hook(d: dict):
            if d["status"] == "downloading":
                try:
                    progress = (
                        d.get("downloaded_bytes", 0)
                        / d.get("total_bytes", 1)
                        * 100
                    )
                except Exception:
                    return

                speed = d.get("speed") or 0
                eta = d.get("eta") or 0

                if not speed:
                    return

                progress_data = {
                    "progress": f"{progress:.1f}%",
                    "speed": f"{speed / 1024 / 1024:.1f} MB/s",
                    "eta": f"{eta // 60}:{eta % 60:02d}",
                    "ext": d.get("filename", "").split(".")[-1],
                }
                asyncio.run(
                    send_progress(
                        CustomWebsocketResponse(
                            status="downloading", detail=progress_data
                        )
                    )
                )

            elif d["status"] == "finished":
                filename = d.get("filename", "").split("/")[-1]
                asyncio.run(
                    send_progress(
                        CustomWebsocketResponse(
                            status="finished", detail=dict(filename=filename)
                        )
                    )
                )

        @silence_websocket_exceptions
        def initiate_download() -> models.MediaDownloadResponse:
            try:
                return real_download_process(
                    request=websocket,
                    payload=request_payload,
                    progress_hooks=[progress_hook],
                )
            except HTTPException as e:
                asyncio.run(
                    send_progress(
                        CustomWebsocketResponse(
                            status="error",
                            detail=dict(status_code=e.status_code, text=e.detail),
                        )
                    )
                )

        download_report = await asyncio.get_running_loop().run_in_executor(
            None, initiate_download
        )
        if isinstance(download_report, models.MediaDownloadResponse):
            await send_progress(
                CustomWebsocketResponse(
                    status="completed", detail=download_report.model_dump()
                )
            )
        else:
            await close_websocket()

    except ValidationError as e:
        error = CustomWebsocketResponse(
            status="error", detail=dict(errors=json.loads(e.json()))
        )
        await send_progress(error)
        await close_websocket()

    except Exception as e:
        logger.error(f"Websocket error {e}")
        await close_websocket()
