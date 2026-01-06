<h1 align="center">YouTube Video Downloader API</h1>


<p align="center">
<a href="LICENSE"><img alt="License" src="https://img.shields.io/static/v1?logo=license&color=Blue&message=Unlicense&label=License"/></a>
<a href="https://github.com/Simatwa/youtube-downloader-api/releases"><img src="https://img.shields.io/github/v/release/Simatwa/youtube-downloader-api?label=Release&logo=github" alt="Latest release"></img></a>
<!--
<a href="https://github.com/Simatwa/youtube-downloader-api/releases"><img src="https://img.shields.io/github/release-date/Simatwa/youtube-downloader-api?label=Release date&logo=github" alt="release date"></img></a>
-->
<a href="https://github.com/psf/black"><img alt="Black" src="https://img.shields.io/badge/code%20style-black-000000.svg"/></a>
<a href="https://github.com/Simatwa/youtube-downloader-api"><img src="https://hits.sh/github.com/Simatwa/youtube-downloader-api.svg?label=Total%20hits&logo=dotenv" alt="Total hits"/></a>
</p>

## Overview

A REST-API that provide endpoints for searching, extracting metadata and downloading YouTube videos in mp4, webm, m4a and mp3 formats in different qualities.

## Prerequisites

- [Python version 3.10 or higher](https://python.org)
- [Git](https://git-scm.com/)

## Installation Guide

Follow these steps to install and configure the YouTube video downloader:

### Step 1: Clone Repository

First, clone the repository using the following command:

```sh
git clone https://github.com/Simatwa/youtube-downloader-api.git
cd youtube-downloader
```

### Step 2: Set Up Virtual Environment

Next, create and activate a virtual environment:

```sh
pip install uv
uv venv
source .venv/bin/activate
```

After activating the virtual environment, install the required dependencies:

```sh
uv pip install -r requirements-all.txt
```

> [!TIP]
> Its good to update yt-dlp version `uv pip install -U yt-dlp`

### Step 3: Configure Environment Variables

Copy any of [configs/env/*](../configs/env/) file to the root directory of the project and rename it to `.env`. Edit the `.env` file to set up your environment variables according to your needs.

> [!WARNING]
> Some of the settings in the `.env` file are very sensitive to the app. A slight change can have a significant impact on the apps's functionality. Ensure you're in good knowledge of the changes you will be making.

### Step 4: Start the Server

Finally, start the server using the following command:

```sh
python -m app run
```

The docs will be accessible from  <http://localhost:8000/api/docs> and redocs from <http://localhost:8000/api/redoc>

> [!TIP]
> For a more smoother control over the server's startup, consider using the FastAPI's cli.
> Running `$ fastapi run app` will equally fire-up the server.
> For more help info such as changing **host** and **port**, you can simply run `$ fastapi run --help`.

## Serving frontend contents

In order to serve frontend contents, you have to pass directory containing the contents to the app using `frontend_dir` key in the [configuration file](../configs/env/example).

> [!NOTE]
> The frontend directory should contain `index.html` file.

## Optimizing Server Performance

To improve server performance and minimize load, I recommend setting up a separate server for handling static contents (audios and videos). To do this:

1. Execute the [`static-server`](../servers/static.py) file.
2. Configure the API using the `static_server_url` key with the URL of the static server.

> [!IMPORTANT]
> It's recommened to use a [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) to serve the static contents at production environment. This [uwsgi.sh](../uwsgi.sh) file might come handy in this.

## Troubleshooting

### Authorization Issues

YouTube flags requests without proper authorization. To work around this issue:

1. Use cookies and po_token as authorized workarounds.
2. Alternatively, use a whitelisted proxy.

> [!NOTE]
> While using a proxy is a straightforward solution, there's no guarantee that the request will go through successfully.

## Utility Servers

1. [Static Server](../servers/static.py)
2. [Proxy Server](../servers/proxy.py)

## Web-Interfaces

The following projects provide web-interfaces for interacting with Youtube-Downloader-API

| Index  |  🎁 Projects  | ⭐ Stars                       |
|--------| ------------- |-------------------------------|
| 0      | [y2mate-clone](https://github.com/Simatwa/y2mate-clone) |  [![Stars](https://img.shields.io/github/stars/Simatwa/y2mate-clone?style=flat-square&labelColor=343b41)](https://github.com/Simatwa/y2mate-clone/stargazers) |

_Feel free to add another web-interface to this list._

## Additional Resources

For detailed information on extracting PO Tokens, refer to the following resource:

[How to extract PO Token](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#po-token-guide)

## License

- [x] [The Unlicense](LICENSE)
