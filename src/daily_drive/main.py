from random import shuffle
from secrets import choice

import spotipy

from daily_drive.config import Settings
from daily_drive.core.auth import Auth
from daily_drive.core.logging import setup_logger
from services.playlist_service import PlaylistService
from services.podcast_service import PodcastService
from services.user_service import UserService

"""
At 6AM GMT -3, every day, the playlist must have this structure:
[
    track,
    SEGUNDOS_123_EPISODE,
    track,
    track,
    CAFE_DA_MANHA_EPISODE,
    track,
    track,
    BOLETIM_FOLHA_EPISODE,
    track,
    track,
    O_ASSUNTO_EPISODE,
    track,
    track,
    NOTICIA_NO_SEU_TEMPO_EPISODE,
    track,
    track,
    PANORAMA_CBN_EPISODE,
    track,
    track,
    RESUMAO_DIARIO_EPISODE,
    track,
    track,
    track,
    track,
    track,
    track,
    track,
    track,
    track,
    track
]
"""


def _start_services(sp: spotipy.Spotify) -> tuple[PlaylistService, UserService, PodcastService]:
    playlist_service = PlaylistService(sp)
    user_service = UserService(sp)
    podcast_service = PodcastService(sp)
    return playlist_service, user_service, podcast_service


def _random_time_range() -> str:
    return choice(["short_term", "medium_term", "long_term"])


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

    playlist_service, user_service, podcast_service = _start_services(sp)
    log.info("Services initialized successfully.")

    # Get top tracks
    tracks = user_service.get_user_top_tracks(
        time_range=_random_time_range(),
        limit=23
    )
    shuffle(tracks)
    log.info(f"Retrieved {len(tracks)} top tracks for the user.")

    # Get podcast episodes
    podcast_episodes = []
    for podcast in playlist_service.PODCASTS.values():
        episode = podcast_service.get_last_podcast_episode(podcast=podcast)
        if episode:
            podcast_episodes.append(episode)
        else:
            log.warning(f"Episode for podcast '{podcast.name}' not found.")

    log.info(
        f"Retrieved {len(podcast_episodes)} podcast episodes for the user.")

    # Create/update daily drive playlist
    result = playlist_service.create_daily_drive_playlist(
        tracks, podcast_episodes)
    log.info(result)


if __name__ == "__main__":
    main()
