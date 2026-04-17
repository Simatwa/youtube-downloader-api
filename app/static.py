"""This module contains code for serving static contents using flask framework"""

from os import getcwd
from pathlib import Path
from urllib.parse import unquote

from flask import Flask, request, send_from_directory

from app.config import DOWNLOAD_DIR

app = Flask(__name__)
static_app = app

ref_directory = (
    DOWNLOAD_DIR
    if DOWNLOAD_DIR.is_absolute()
    else Path(getcwd()).joinpath(DOWNLOAD_DIR)
)


@app.get("/file/<path:name>")
def send_static_file(name):
    download = request.args.get("download", "0") in ("1", "true")
    return send_from_directory(ref_directory, unquote(name), as_attachment=download)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="y2mate-clone-static-server",
        description="Server for static contents ie. audio and video",
        epilog="For production environment use uwsgi.",
    )
    parser.add_argument(
        "-ho",
        "--host",
        help="Interface to bind to - %(default)s.",
        default="127.0.0.1",
    )
    parser.add_argument(
        "-p", "--port", help="Port to listen at - %(default)d", default=8080
    )
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=False)
