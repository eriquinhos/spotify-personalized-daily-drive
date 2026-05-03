from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: str
    name: str
    uri: str
    url: str
    email: str | None = None
    images: list[str] | None = None
