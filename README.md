<h1 align="center">YouTube Video Downloader</h1>

## Overview

This document provides a step-by-step guide for installing and using the YouTube video downloader application. The tool allows users to download YouTube videos in mp4, webm, and mp3 formats.

## Prerequisites

- [Python version 3.10 or higher](https://python.org)
- [Git](https://git-scm.com/)

## Installation Guide

> [!NOTE]
> This guide assumes you're running on a *nix system.

Follow these steps to install and configure the YouTube video downloader:

### Step 1: Clone Repository

First, clone the repository using the following command:

```sh
git clone https://github.com/Simatwa/youtube-downloader.git
cd youtube-downloader
```

### Step 2: Set Up Virtual Environment

Next, create and activate a virtual environment:

```sh
pip install virtualenv
virtualenv venv
source venv/bin/activate
```

After activating the virtual environment, install the required dependencies:

```sh
make install
```

### Step 3: Configure Environment Variables

Create a copy of the `.env.example` file and rename it to `.env`. Edit the `.env` file to set up your environment variables according to your needs.

> [!WARNING]
> Some of the settings in the `.env` file are very sensitive to the app. A slight change can have a significant impact on the apps's functionality. Ensure you're in good knowledge of the changes you will be making.

### Step 4: Start the Server

Finally, start the server using the following command:

```sh
make runserver
```

## Optimizing Server Performance

To improve server performance and minimize load, I recommend setting up a separate server for handling static contents (audios and videos). To do this:

1. Execute the `static_server.py` file.
2. Configure the API using the `static_server_url` key with the URL of the static server.

## Troubleshooting

### Authorization Issues

YouTube flags requests without proper authorization. To work around this issue:

1. Use cookies and po_token as authorized workarounds.
2. Alternatively, use a proxy from a location exempted from required authorizations (e.g., Canada).

> [!NOTE]
> While using a proxy is a straightforward solution, there's no guarantee that the request will go through successfully.

## Additional Resources

For detailed information on extracting PO Tokens, refer to the following resource:

[How to extract PO Token](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#po-token-guide)

## License

- [x] [The Unlicense](LICENSE)
