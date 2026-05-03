from pathlib import Path
from typing import ClassVar
import base64

import spotipy

from daily_drive.models.episode import Episode
from daily_drive.models.playlist import Playlist
from daily_drive.models.podcast import Podcast
from daily_drive.models.track import Track
from daily_drive.models.user import User
from services.user_service import UserService


class PlaylistService:
    # Podcasts da Daily Drive
    PODCASTS: ClassVar[dict] = {
        "123_segundos": Podcast(
            id="4Z5CoK9UJq3ykgLbcBTQwP",
            key="123_segundos",
            name="123 Segundos"
        ),
        "cafe_da_manha": Podcast(
            id="6WRTzGhq3uFxMrxHrHh1lo",
            key="cafe_da_manha",
            name="Café da Manhã"
        ),
        "boletim_folha": Podcast(
            id="45PqwRAJBEOdNc28ijJnIz",
            key="boletim_folha",
            name="Boletim Folha"
        ),
        "o_assunto": Podcast(
            id="4gkKyFdZzkv1eDnlTVrguk",
            key="o_assunto",
            name="O Assunto"
        ),
        "noticia_no_seu_tempo": Podcast(
            id="3M3xXhNXudIXGNSrjvoETG",
            key="noticia_no_seu_tempo",
            name="Notícia no Seu Tempo"
        ),
        "panorama_cbn": Podcast(
            id="3mKy8vUlAHoLxZVaILsUWw",
            key="panorama_cbn",
            name="Panorama CBN"
        ),
        "resumao_diario": Podcast(
            id="7fzhxpt0RgWaLFYydsv2b4",
            key="resumao_diario",
            name="Resumão Diário"
        ),
    }

    # Ordem dos podcasts na playlist (conforme estrutura comentada)
    PODCAST_ORDER: ClassVar[list] = [
        "4Z5CoK9UJq3ykgLbcBTQwP",           # 123_segundos
        "6WRTzGhq3uFxMrxHrHh1lo",           # cafe_da_manha
        "45PqwRAJBEOdNc28ijJnIz",           # boletim_folha
        "4gkKyFdZzkv1eDnlTVrguk",           # o_assunto
        "3M3xXhNXudIXGNSrjvoETG",           # noticia_no_seu_tempo
        "3mKy8vUlAHoLxZVaILsUWw",           # panorama_cbn
        "7fzhxpt0RgWaLFYydsv2b4",           # resumao_diario
    ]

    def __init__(self, sp: spotipy.Spotify) -> None:
        self.sp = sp
        self.user_service = UserService(self.sp)

    def _check_existing_playlist(self, user: User, name: str) -> str | None:
        user_playlists = self.user_service.get_user_playlists(limit=100)
        for playlist in user_playlists:
            if playlist.name == name:
                return playlist.id
        return None

    def add_tracks_to_playlist(self, playlist: Playlist, tracks: list[Track]) -> str:
        track_uris = [track.uri for track in tracks]
        try:
            self.sp.playlist_add_items(playlist.id, track_uris)
            return f"Added {len(tracks)} tracks to playlist '{playlist.name}'."
        except spotipy.SpotifyException as e:
            return f"Error adding tracks to playlist: {e}"

    def add_episodes_to_playlist(self, playlist: Playlist, episodes: list[Episode]) -> str:
        episode_uris = [episode.uri for episode in episodes]
        try:
            self.sp.playlist_add_items(playlist.id, episode_uris)
            return f"Added {len(episodes)} episodes to playlist '{playlist.name}'."
        except spotipy.SpotifyException as e:
            return f"Error adding episodes to playlist: {e}"

    import base64


    def _add_image_to_playlist(self, playlist_id: str, image_path: str) -> str:
        try:
            with open(image_path, "rb") as img_file:
                img_data = img_file.read()
            # Convert to base64 bytes
            img_b64 = base64.b64encode(img_data)
            self.sp.playlist_upload_cover_image(playlist_id, img_b64)
            return f"Image '{image_path}' uploaded successfully to playlist ID: {playlist_id}"
        except FileNotFoundError:
            return f"Image file '{image_path}' not found."
        except spotipy.SpotifyException as e:
            return f"Error uploading image to playlist: {e}"

    def _build_structured_uris(
        self,
        tracks: list[Track],
        episodes: list[Episode],
        episodes_by_podcast: dict
    ) -> list[str]:
        """Build the ordered list of URIs following the daily drive structure."""
        structured_uris = []
        track_uris = [t.uri for t in tracks]
        track_index = 0

        # Primeiro: 1 track + 1 episode
        if track_index < len(track_uris):
            structured_uris.append(track_uris[track_index])
            track_index += 1

        first_podcast = self.PODCAST_ORDER[0]
        if episodes := episodes_by_podcast.get(first_podcast):
            structured_uris.append(episodes.pop(0).uri)

        # Blocos restantes: 2 tracks + 1 episode
        for podcast_id in self.PODCAST_ORDER[1:]:
            for _ in range(2):
                if track_index < len(track_uris):
                    structured_uris.append(track_uris[track_index])
                    track_index += 1

            if episodes := episodes_by_podcast.get(podcast_id):
                structured_uris.append(episodes.pop(0).uri)

        # Adicionar tracks restantes
        while track_index < len(track_uris):
            structured_uris.append(track_uris[track_index])
            track_index += 1

        return structured_uris

    def _add_structured_content_to_playlist(
        self,
        playlist: Playlist,
        tracks: list[Track],
        episodes: list[Episode]
    ) -> str:
        """
        Add tracks and episodes to playlist following the daily drive structure.
        Structure: 1 track, SEGUNDOS_123 episode, 2 tracks, CAFE_DA_MANHA episode, ...
        """
        # Mapear episodes por podcast.id
        episodes_by_podcast = {}
        for episode in episodes:
            podcast_id = episode.podcast.id
            if podcast_id not in episodes_by_podcast:
                episodes_by_podcast[podcast_id] = []
            episodes_by_podcast[podcast_id].append(episode)

        structured_uris = self._build_structured_uris(
            tracks, episodes, episodes_by_podcast)

        try:
            self.sp.playlist_add_items(playlist.id, structured_uris)
            return f"Added {len(tracks)} tracks and {len(episodes)} episodes to playlist '{playlist.name}'."
        except spotipy.SpotifyException as e:
            return f"Error adding content to playlist: {e}"

    def _refresh_existing_playlist(
        self,
        playlist_id: str,
        tracks: list[Track],
        episodes: list[Episode]
    ) -> str:
        root_path = Path(__file__).parents[1]
        image_path = root_path / "daily_drive" / \
            "assets" / "images" / "daily_drive.jpg"
        try:
            self.sp.playlist_replace_items(playlist_id, [])
            playlist_data = self.sp.playlist(playlist_id)
            self._add_image_to_playlist(playlist_id, str(image_path))
            playlist = Playlist(
                id=playlist_data["id"],
                name=playlist_data["name"],
                tracks=[],
                owner=None,
                public=playlist_data.get("public", True),
                uri=playlist_data["uri"],
                url=playlist_data["external_urls"]["spotify"]
            )
            return self._add_structured_content_to_playlist(playlist, tracks, episodes)
        except spotipy.SpotifyException as e:
            return f"Error refreshing playlist: {e}"

    def create_daily_drive_playlist(self, tracks: list[Track], episodes: list[Episode]) -> str:
        root_path = Path(__file__).parents[1]
        image_path = root_path / "daily_drive" / \
            "assets" / "images" / "daily_drive.jpg"
        user = self.user_service.get_user_info()
        playlist_name = "Personal Daily Drive"
        existing_playlist_id = self._check_existing_playlist(
            user, playlist_name)

        if existing_playlist_id:
            return self._refresh_existing_playlist(existing_playlist_id, tracks, episodes)

        try:
            playlist_data = self.sp.user_playlist_create(
                user.id, playlist_name, public=True)
            playlist = Playlist(
                id=playlist_data["id"],
                name=playlist_data["name"],
                tracks=[],
                owner=None,
                public=playlist_data.get("public", True),
                uri=playlist_data["uri"],
                url=playlist_data["external_urls"]["spotify"]
            )
            self._add_image_to_playlist(playlist_data["id"], str(image_path))
            self._add_structured_content_to_playlist(playlist, tracks, episodes)
            return f"Playlist '{playlist_name}' created successfully with ID: {playlist_data['id']}"
        except spotipy.SpotifyException as e:
            return f"Error creating playlist: {e}"
