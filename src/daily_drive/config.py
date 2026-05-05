import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import dotenv
import yaml

from daily_drive.models.podcast import Podcast
from services.podcast_service import PodcastService

dotenv.load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def _load_yaml_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}

    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        loaded_config = yaml.safe_load(config_file) or {}

    return loaded_config if isinstance(loaded_config, dict) else {}


YAML_CONFIG = _load_yaml_config()


def _get_config_int(name: str, default: int) -> int:
    daily_drive_config = YAML_CONFIG.get("daily_drive", {})
    if not isinstance(daily_drive_config, dict):
        return default

    raw_value = daily_drive_config.get(name, default)
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return default

def _get_env_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value.strip() == "":
        return default

    try:
        return int(raw_value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    spotify_client_id: str | None = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_client_secret: str | None = os.getenv("SPOTIFY_CLIENT_SECRET")
    spotify_redirect_uri: str | None = os.getenv("SPOTIFY_REDIRECT_URI")
    spotify_scope: str = (
        "playlist-modify-public playlist-modify-private "
        "user-library-read user-top-read ugc-image-upload"
    )
    daily_drive_tracks_after_welcome: int = _get_env_int(
        "DAILY_DRIVE_TRACKS_AFTER_WELCOME",
        _get_config_int("tracks_after_welcome", 2),
    )
    daily_drive_tracks_between_episodes: int = _get_env_int(
        "DAILY_DRIVE_TRACKS_BETWEEN_EPISODES",
        _get_config_int("tracks_between_episodes", 4),
    )
    daily_drive_final_tracks: int = _get_env_int(
        "DAILY_DRIVE_FINAL_TRACKS",
        _get_config_int("final_tracks", 10),
    )
    podcasts: list[Podcast] = field(
        default_factory=lambda: PodcastService.load_podcasts_from_config(YAML_CONFIG))
