# Utility Servers

## 1. [Static Server](./static_server.py)

The sole purpose of this is to reduce the work-load on youtube-downloader API.
Allows the API to only serve the dynamic contents as it focuses on static ones.

### Usage:

`$ python -m servers.static`

<details open>

<summary>

<code> $ python -m servers.static --help </code>


</summary>

```
usage: y2mate-clone-static-server [-h] [-ho HOST] [-p PORT]

Server for static contents ie. audio and video

options:
  -h, --help        show this help message and exit
  -ho, --host HOST  Interface to bind to - 127.0.0.1.
  -p, --port PORT   Port to listen at - 8888

For production environment use uwsgi.

```

</details>

## 2. [Proxy Server](./proxy_server.py)

Hosting web-interface over https makes http (insecure) API calls to fail except to localhost.
So this script links the two; a youtube-downloader API accessible over http and a web-interface that's
accessible securely (https).

### Steps

1. Host youtube-downloader over http (insecure)
2. Start this proxy (locally) and point base_url to the address of youtube-downloader
3. Point API-BASE-URL in web-interface to proxy's address.

### Usage:

`$ python -m servers.proxy http://localhost:8000/`

<details open>

<summary>

<code> $ python -m servers.proxy --help </code>

</summary>

```
usage: y2mate-clone-proxy [-h] [-ho HOST] [-p PORT] [-t TIMEOUT] base_url

Proxy for y2mate-clone. Meant to forward request to and fro an insecure API

positional arguments:
  base_url              Y2mate-clone API base url.

options:
  -h, --help            show this help message and exit
  -ho, --host HOST      Interface to bind to - 127.0.0.1.
  -p, --port PORT       Port to listen at - 8080
  -t, --timeout TIMEOUT
                        API request call timeout in minutest - 30

Not meant for production purposes.

```

</details>

> [!IMPORTANT]
> Running these scripts over [uwsgi](https://pypi.org/project/uWSGI/) is always recommended especially in production environment.