from dataclasses import dataclass

from daily_drive.models.artist import Artist


@dataclass(frozen=True)
class Track:
    id: str
    name: str
    artists: list[Artist]
    album_id: str
    release_date: str
    uri: str
    url: str
    explicit: bool = False
    duration_ms: int | None = None
