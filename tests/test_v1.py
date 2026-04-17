import pytest

import app.v1.models as models
from tests import client

video_link = (
    "https://youtu.be/S3wsCRJVUyg?si=SjN17MR1-u7BPgxk?si=svRtQPHef9TSMABt"
)
# https://youtu.be/R3GfuzLMPkA?si=YItOxtgw3LAjKps1


@pytest.mark.parametrize(["query", "limit"], [("hello", 2), ("hey", 1)])
def test_video_search(query, limit):
    resp = client.get("/api/v1/search", params=dict(q=query, limit=limit))
    assert resp.is_success
    videos = models.SearchVideosResponse(**resp.json())
    assert len(videos.results) <= limit


@pytest.mark.parametrize(
    ["url"],
    [
        ("https://youtu.be/HUGcwe93F9E?si=Ajunj8GlRs-DzKnQ",),
        ("HUGcwe93F9E",),
        ("https://www.youtube.com/watch?v=HUGcwe93F9E",),
    ],
)
def test_video_metadata(url):
    resp = client.get("/api/v1/metadata", params=dict(url=url))
    assert resp.is_success
    models.VideoMetadataResponse(**resp.json())


@pytest.mark.parametrize(
    ["url", "quality", "bitrate"],
    [
        ("https://youtu.be/S3wsCRJVUyg?si=SjN17MR1-u7BPgxk", "1080p", None),
        ("https://youtu.be/S3wsCRJVUyg?si=SjN17MR1-u7BPgxk", "720p", "128k"),
        ("https://youtu.be/S3wsCRJVUyg?si=SjN17MR1-u7BPgxk", "medium", "192k"),
        ("https://youtu.be/S3wsCRJVUyg?si=SjN17MR1-u7BPgxk", "medium", None),
    ],
)
def test_download_processing(url, quality, bitrate):
    resp = client.post(
        "/api/v1/download",
        json=dict(
            url=url,
            quality=quality,
            bitrate=bitrate,
        ),
    )
    if not resp.is_success:
        print(resp.text)
    assert resp.is_success
    models.MediaDownloadResponse(**resp.json())
    # This will raise 404 since the static contents are served by flask (wsgi).
    # static_resp = client.get(str(media.link))
    # assert static_resp.is_success
