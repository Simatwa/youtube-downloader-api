"""Youtube downloader API"""

import time
from contextlib import asynccontextmanager

from a2wsgi import WSGIMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import loaded_config, pyproject_dot_toml_details
from app.events import (
    create_temp_dirs,
    event_clear_previous_downloads,
    event_create_tables,
    event_delete_expired_extracted_info,
)
from app.models import ConfigModel
from app.static import static_app
from app.utils import logger

create_temp_dirs()

project_details = pyproject_dot_toml_details["project"]

from app.v1 import v1_router  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    # create_temp_dirs()
    event_create_tables()
    event_delete_expired_extracted_info()

    yield

    # shutdown
    event_clear_previous_downloads()
    event_delete_expired_extracted_info()


app = FastAPI(
    title=loaded_config.api_title,
    version=project_details["version"],
    summary=project_details["description"],
    description=loaded_config.api_description,
    terms_of_service=str(loaded_config.api_terms_of_service),
    contact=loaded_config.contacts,
    license_info={
        "name": "GPLv3",
        "url": "https://raw.githubusercontent.com/Simatwa/"
        "youtube-downloader-api/refs/heads/main/LICENSE",
    },
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.include_router(v1_router, prefix="/api", tags=["v1"])

if not loaded_config.static_server_url:
    app.mount("/static", WSGIMiddleware(static_app, workers=50))


@app.get("/api/config", include_in_schema=False)
def get_app_config() -> ConfigModel:
    """Get current running app configuration"""
    return loaded_config


@app.get("/api/health", include_in_schema=False)
def test_live():
    """Check API's live status"""
    return {}


if (
    loaded_config.frontend_dir
    and not loaded_config.serve_frontend_from_static_server
):
    # Lets's serve the frontend from /
    logger.info(f"Serving frontend. Frontend dir: {loaded_config.frontend_dir}")
    app.mount(
        "/",
        StaticFiles(
            directory=loaded_config.frontend_dir, check_dir=True, html=True
        ),
        name="frontend",
    )

else:
    # Redirect / to docs
    logger.info("Not serving frontend. Redirecting / to /api/docs")

    @app.get("/", include_in_schema=False)
    async def home():
        return RedirectResponse("/api/docs")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def add_cache_header(request: Request, call_next):
    """Browsers to cache the response for 30 minutes"""
    response: Response = await call_next(request)
    if response.status_code == 200:
        """
        if request.url.path.startswith("/api/v1"):
            response.headers["Cache-Control"] = "public, max-age=1800"
        else:
            # static contents
            response.headers["Cache-Control"] = "public, max-age=86400"
        """
        response.headers["Cache-Control"] = "public, max-age=86400"

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
