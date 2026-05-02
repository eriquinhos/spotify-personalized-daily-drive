# src/daily_drive/main.py
from daily_drive.config import Settings
from daily_drive.core.auth import Auth
from daily_drive.core.logging import setup_logger


def main() -> None:
    log = setup_logger()
    settings = Settings()

    if not settings.spotify_client_id or not settings.spotify_client_secret:
        log.error("Spotify credentials not found.")
        return

    auth = Auth(
        settings.spotify_client_id,
        settings.spotify_client_secret,
        settings.spotify_redirect_uri,
        settings.spotify_scope,
    )
    sp = auth.authenticate()
    log.info("Successfully authenticated with Spotify API.")
