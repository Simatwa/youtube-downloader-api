from datetime import datetime, timedelta
from json import loads

from sqlmodel import Column, Field, Session, SQLModel, Text, create_engine
from yt_dlp_bonus.models import ExtractedInfo

from app.config import loaded_config
from app.utils import utc_now

engine = create_engine(url=loaded_config.database_engine)

video_info_cache_period = timedelta(
    hours=loaded_config.video_info_cache_period_in_hrs
)


class VideoInfo(SQLModel, table=True):
    id: str | None = Field(
        default=None, primary_key=True, description="Youtube video id"
    )
    info: str = Field(
        sa_column=Column(Text, default=None, nullable=False),
        description="Video info_dict",
    )
    updated_on: datetime = Field(
        default_factory=utc_now, description="Last time to be updated"
    )

    @property
    def is_valid(self) -> bool:
        """Checks if the current info is still relevant"""
        return (utc_now() - self.updated_on) <= video_info_cache_period

    @property
    def extracted_info(self) -> ExtractedInfo:
        return ExtractedInfo(**loads(self.info))


def create_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(bind=engine)


def get_session():
    """Database session"""
    with Session(engine) as session:
        yield session
