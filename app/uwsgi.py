# /usr/bin/python3
"""
Converts fastapi app to wsgi app

uv run --active uwsgi --http=0.0.0.0:8080 -w app.uwsgi:application
"""

from a2wsgi import ASGIMiddleware

from app import app

application = ASGIMiddleware(app)
