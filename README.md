<div align="center">

# YouTube Video Downloader API

[![License](https://img.shields.io/static/v1?logo=license&color=Blue&message=Unlicense&label=License)](LICENSE)
[![Release](https://img.shields.io/github/v/release/Simatwa/youtube-downloader-api?label=Release&logo=github)](https://github.com/Simatwa/youtube-downloader-api/releases)
[![Release date](https://img.shields.io/github/release-date/Simatwa/youtube-downloader-api?label=Release%20date&logo=github)](https://github.com/Simatwa/youtube-downloader-api/releases)
[![Total hits](https://hits.sh/github.com/Simatwa/youtube-downloader-api.svg?label=Total%20hits)](https://github.com/Simatwa/youtube-downloader-api)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
</div>


A REST API that provides endpoints for searching, extracting metadata, and downloading YouTube videos in **mp4**, **webm**, **m4a**, and **mp3** formats across multiple quality levels. It is built on FastAPI and powered by `yt-dlp` under the hood, making it suitable for both local use and production deployment.

## Prerequisites

Before getting started, ensure the following are installed on your system:

- [Python 3.10 or higher](https://python.org) — the runtime environment
- [Git](https://git-scm.com/) — for cloning the repository

## Installation Guide

### Step 1: Clone the Repository

Clone the project and navigate into the project directory:

```sh
git clone https://github.com/Simatwa/youtube-downloader-api.git
cd youtube-downloader
```

### Step 2: Set Up a Virtual Environment

Create and activate a virtual environment, then install all dependencies:

```sh
pip install uv
uv venv
source .venv/bin/activate
uv sync
```

> [!TIP]
> It is strongly recommended to keep `yt-dlp` updated regularly to avoid breakage caused by YouTube-side changes:
> ```sh
> uv pip install -U yt-dlp
> ```

### Step 3: Configure Settings (Optional)

By default, the app loads configuration from [`config.yml`](./config.yml). Review and adjust the values to suit your environment before starting the server.

For a quick production-ready setup, a pre-tuned [`production.yml`](./production.yml) is included. Simply rename it to `config.yml` to use it:

```sh
mv production.yml config.yml
```

> [!WARNING]
> Some settings in `config.yml` are critical to the app's operation. Incorrect values can break functionality entirely. Make changes only when you understand their effect.

### Step 4: Start the Server

Launch the development server with:

```sh
uv run python -m app run
```

Alternatively, use FastAPI's CLI for more control:

```sh
fastapi run app
```

For advanced startup options such as changing the **host** or **port**:

```sh
uv run fastapi run --help
```

Once running, the API documentation is available at:

- **Swagger UI:** <http://localhost:8000/api/docs>
- **ReDoc:** <http://localhost:8000/api/redoc>

## Serving Frontend Contents

The API can serve a static frontend alongside the backend. To enable this, set the `frontend_dir` key in your [configuration file](./config.yml) to the path of the directory containing your frontend build.

> [!NOTE]
> The specified frontend directory **must** contain an `index.html` file at its root. Without it, the frontend will not be served correctly.

## Optimizing Server Performance

For production deployments, offloading static file delivery (downloaded audio and video files) to a dedicated static server significantly reduces load on the main API process.

**Setup steps:**

1. Start the included static file server:
```sh
   python servers/static.py
```
2. Set the `static_server_url` key in `config.yml` to point to the static server's URL.

> [!IMPORTANT]
> In production, it is recommended to serve static content using [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) for better concurrency and stability. The included [`uwsgi.sh`](../uwsgi.sh) script provides a ready-to-use uWSGI configuration to get you started quickly.

## Troubleshooting

### Authorization Issues

YouTube actively flags and blocks requests that lack proper browser-like authorization context. This is a common cause of download failures, especially on fresh deployments or IPs with no prior request history.

**Recommended workarounds:**

1. **Cookies + PO Token** - Extract your browser cookies and a valid `po_token`, then pass them to the app. This is the most reliable method. See the full guide:
   [How to extract PO Token](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#po-token-guide)

2. **Whitelisted Proxy** - Route requests through a proxy server that YouTube has not flagged.

> [!NOTE]
> Using a proxy does not guarantee success. YouTube's detection mechanisms can flag proxy IPs as well. The cookie + PO token approach is generally more stable.

## Utility Servers

Two helper servers are included for extending the API's capabilities in production:

| Server | Description |
|--------|-------------|
| [Static Server](../servers/static.py) | Serves downloaded media files independently from the main API process, reducing load and improving throughput |
| [Proxy Server](../servers/proxy.py) | Forwards requests to a non-HTTPS instance of the YouTube Downloader API hosted on a remote server |

## Web Interfaces

The following projects provide ready-to-use web frontends for interacting with the YouTube Downloader API:

| Index | 🎁 Project | ⭐ Stars |
|-------|-----------|---------|
| 0 | [y2mate-clone](https://github.com/Simatwa/y2mate-clone) | [![Stars](https://img.shields.io/github/stars/Simatwa/y2mate-clone?style=flat-square&labelColor=343b41)](https://github.com/Simatwa/y2mate-clone/stargazers) |

_Built a frontend that works with this API? Feel free to open a PR and add it to this list._

## Additional Resources

- [How to extract PO Token](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#po-token-guide) — Required reading if you encounter YouTube authorization errors
- [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp) - The underlying download engine powering this API
- [uWSGI documentation](https://uwsgi-docs.readthedocs.io/en/latest/) - Recommended for production static file serving

## License

- [x] [The Unlicense](LICENSE)