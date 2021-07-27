from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class InstagramPostItems:
    is_video: bool
    url: str
    video_prev: str


@dataclass
class InstagramPost:
    is_video: bool
    is_slider: bool
    items: Optional[list[InstagramPostItems]]
    url: str
    video_prev: Optional[str]
    datetime: datetime
    post_id: str
    post_url: str
    description: str
