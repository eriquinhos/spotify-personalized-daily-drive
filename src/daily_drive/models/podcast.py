from dataclasses import dataclass


@dataclass(frozen=True)
class Podcast:
    id: str
    key: str
    name: str
    publisher: str | None = None
