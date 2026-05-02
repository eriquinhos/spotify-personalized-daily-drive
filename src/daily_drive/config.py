import os
from dataclasses import dataclass

import dotenv

dotenv.load_dotenv()


@dataclass(frozen=True)
class Settings:
    spotify_client_id: str | None = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_client_secret: str | None = os.getenv("SPOTIFY_CLIENT_SECRET")
    spotify_redirect_uri: str | None = os.getenv("SPOTIFY_REDIRECT_URI")
    spotify_scope: str = "playlist-modify-public playlist-modify-private user-library-read"
    market: str = "BR"
