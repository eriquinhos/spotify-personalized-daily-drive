from dataclasses import dataclass

from daily_drive.models.artist import Artist
from daily_drive.models.track import Track


@dataclass(frozen=True)
class Album:
    id: str
    name: str
    artists: list[Artist]
    release_date: str
    tracks: list[Track]
    uri: str
    url: str
    total_tracks: int | None = None
