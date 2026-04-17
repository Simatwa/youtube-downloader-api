#!/usr/bin/bash

target_server=$1

if [ "$target_server" == "proxy" ]; then
   echo "[INFO] To daemonize process use : make uwsgi-proxy"
   echo "[PROXY] Running on 0.0.0.0:8080"
   uv run --active uwsgi --http=0.0.0.0:8080 -w servers.proxy:app --enable-threads
elif [ "$target_server" == "static" ]; then
   echo "[INFO] To daemonize process use : make uwsgi-static"
   echo "[STATIC] Running on 0.0.0.0:8888"
   echo "[STATIC] Serving files from static/downloads at /file"
   uv run --active uwsgi --http=0.0.0.0:8888 -w servers.static:app --enable-threads
else
   echo "[ERROR] proxy|static must be explicitly declared"
   echo "        e.g $0 proxy"
   exit 1
fi