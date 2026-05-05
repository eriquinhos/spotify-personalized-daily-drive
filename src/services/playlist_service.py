import base64
from datetime import datetime
from pathlib import Path

import spotipy

from daily_drive.models.artist import Artist
from daily_drive.models.episode import Episode
from daily_drive.models.playlist import Playlist
from daily_drive.models.podcast import Podcast
from daily_drive.models.track import Track
from daily_drive.models.user import User
from services.user_service import UserService


class PlaylistService:
    def __init__(self, sp: spotipy.Spotify, podcasts: list[Podcast] | None = None) -> None:
        self.sp = sp
        self.user_service = UserService(self.sp) if sp else None
        if podcasts:
            self.podcasts = list(podcasts)
        elif sp:
            # If no podcasts provided via config, try to fetch user's top podcasts
            try:
                self.podcasts = self.user_service.get_user_top_podcasts(
                    limit=5)
            except (AttributeError, spotipy.SpotifyException, TypeError):
                # If the SP client is missing methods or Spotify errors, fall back to empty list
                self.podcasts = []
        else:
            self.podcasts = []
        self.podcast_order = [podcast.id for podcast in self.podcasts]

    @classmethod
    def required_track_count(cls, *args: int) -> int:
        """Calculate required number of tracks for the daily drive structure.

        Supports two call styles for backward compatibility:
        - required_track_count(tracks_after_welcome, tracks_between_episodes, final_tracks)-> uses default
        podcast count (5)
        - required_track_count(podcast_count, tracks_after_welcome, tracks_between_episodes, final_tracks)-> uses the
        explicit podcast_count
        """

        if len(args) == 3:
            tracks_after_welcome, tracks_between_episodes, final_tracks = args
            # Default to 5 podcasts when caller omits podcast_count
            podcast_count = 5
        elif len(args) == 4:
            podcast_count, tracks_after_welcome, tracks_between_episodes, final_tracks = args
        else:
            msg = (
                "required_track_count() takes either 3 or 4 positional "
                "arguments"
            )
            raise TypeError(msg)

        if podcast_count <= 0:
            return tracks_after_welcome + final_tracks

        return (
            tracks_after_welcome
            + (podcast_count - 1) * tracks_between_episodes
            + final_tracks
        )

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

    def _add_image_to_playlist(self, playlist_id: str, image_path: str) -> str:
        try:
            with open(image_path, "rb") as img_file:
                img_data = img_file.read()
            # Convert to base64 bytes
            img_b64 = base64.b64encode(img_data)
            self.sp.playlist_upload_cover_image(playlist_id, img_b64)
        except FileNotFoundError:
            return f"Image file '{image_path}' not found."
        except spotipy.SpotifyException as e:
            return f"Error uploading image to playlist: {e}"
        else:
            return f"Image '{image_path}' uploaded successfully to playlist ID: {playlist_id}"

    @staticmethod
    def _append_track_uris(
        structured_uris: list[str],
        track_uris: list[str],
        track_index: int,
        count: int,
    ) -> int:
        for _ in range(count):
            if track_index >= len(track_uris):
                break
            structured_uris.append(track_uris[track_index])
            track_index += 1
        return track_index

    @staticmethod
    def _append_episode_uri(
        structured_uris: list[str],
        episodes_by_podcast: dict,
        podcast_id: str,
    ) -> None:
        if episodes := episodes_by_podcast.get(podcast_id):
            structured_uris.append(episodes.pop(0).uri)

    def build_structured_uris(
        self,
        tracks: list[Track],
        episodes: list[Episode],
        episodes_by_podcast: dict,
        welcome_uri: str | None = None,
        tracks_after_welcome: int = 2,
        tracks_between_episodes: int = 4,
        final_tracks: int = 10,
    ) -> list[str]:
        """Build the ordered list of URIs following the daily drive structure.

        If `welcome_uri` is provided it will be placed before the first music.
        """
        structured_uris: list[str] = []
        track_uris = [t.uri for t in tracks]
        track_index = 0

        # Prepend welcome track if available
        if welcome_uri:
            structured_uris.append(welcome_uri)

        track_index = self._append_track_uris(
            structured_uris,
            track_uris,
            track_index,
            tracks_after_welcome,
        )

        for podcast_index, podcast_id in enumerate(self.podcast_order):
            self._append_episode_uri(
                structured_uris, episodes_by_podcast, podcast_id)

            if podcast_index < len(self.podcast_order) - 1:
                track_index = self._append_track_uris(
                    structured_uris,
                    track_uris,
                    track_index,
                    tracks_between_episodes,
                )

        self._append_track_uris(
            structured_uris, track_uris, track_index, final_tracks)

        return structured_uris

    def _add_structured_content_to_playlist(
        self,
        playlist: Playlist,
        tracks: list[Track],
        episodes: list[Episode],
        tracks_after_welcome: int = 2,
        tracks_between_episodes: int = 4,
        final_tracks: int = 10,
    ) -> str:
        """
        Add tracks and episodes to playlist following the daily drive structure.
        Structure is configurable through track counts around each podcast block.
        """
        # Mapear episodes por podcast.id
        episodes_by_podcast = {}
        for episode in episodes:
            podcast_id = episode.podcast.id
            if podcast_id not in episodes_by_podcast:
                episodes_by_podcast[podcast_id] = []
            episodes_by_podcast[podcast_id].append(episode)

        # Filter out unavailable tracks early so we don't try to add them to playlists.
        try:
            available_tracks, unavailable_tracks = self.user_service.filter_available_tracks(
                tracks
            )
        except (AttributeError, TypeError, ValueError):
            # If filtering fails for any reason (mocks, limited SP client), fall back to original list
            available_tracks, unavailable_tracks = tracks, []

        welcome_uri: str | None = None
        welcome_uri = self._get_welcome_uri()

        structured_uris = self.build_structured_uris(
            available_tracks,
            episodes,
            episodes_by_podcast,
            welcome_uri=welcome_uri,
            tracks_after_welcome=tracks_after_welcome,
            tracks_between_episodes=tracks_between_episodes,
            final_tracks=final_tracks,
        )

        try:
            self.sp.playlist_add_items(playlist.id, structured_uris)
        except spotipy.SpotifyException as e:
            return f"Error adding content to playlist: {e}"
        else:
            msg = (
                f"Added {len(available_tracks)} tracks and {len(episodes)} "
                f"episodes to playlist '{playlist.name}'."
            )
            if unavailable_tracks:
                msg += f" Skipped {len(unavailable_tracks)} unavailable tracks."
            return msg

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

    def create_daily_drive_playlist(
        self,
        tracks: list[Track],
        episodes: list[Episode],
        tracks_after_welcome: int = 2,
        tracks_between_episodes: int = 4,
        final_tracks: int = 10,
    ) -> str:
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
            self._add_structured_content_to_playlist(
                playlist,
                tracks,
                episodes,
                tracks_after_welcome=tracks_after_welcome,
                tracks_between_episodes=tracks_between_episodes,
                final_tracks=final_tracks,
            )
            return f"Playlist '{playlist_name}' created successfully with ID: {playlist_data['id']}"
        except spotipy.SpotifyException as e:
            return f"Error creating playlist: {e}"

    def get_spotify_daily_drive_welcome_tracks(
        self,
        album_id: str = "56DxAA2hEm2S8Lsh1ih9Qq",  # PT default
    ) -> list[Track]:
        """
        Spotify Daily Drive welcome tracks album IDs:
        Portuguese: 56DxAA2hEm2S8Lsh1ih9Qq
        Spanish:    2kpNmUgrzvynwA5u1q8OeV
        """
        results = self.sp.album_tracks(album_id=album_id, limit=50)
        items = results.get("items", [])

        # Handle pagination in case Spotify returns more than one page.
        while results.get("next"):
            results = self.sp.next(results)
            items.extend(results.get("items", []))

        # album_tracks gives simplified tracks; fetch album once for release_date.
        album_data = self.sp.album(album_id)
        release_date = album_data.get("release_date", "")

        mapped_tracks: list[Track] = []
        for t in items:
            artists = [
                Artist(
                    id=a.get("id", ""),
                    name=a.get("name", ""),
                    uri=a.get("uri", ""),
                    url=a.get("external_urls", {}).get("spotify", ""),
                )
                for a in t.get("artists", [])
            ]

            mapped_tracks.append(
                Track(
                    id=t.get("id", ""),
                    name=t.get("name", ""),
                    artists=artists,
                    album_id=album_id,
                    release_date=release_date,
                    uri=t.get("uri", ""),
                    url=t.get("external_urls", {}).get("spotify", ""),
                    explicit=t.get("explicit", False),
                    duration_ms=t.get("duration_ms"),
                )
            )
        return mapped_tracks

    def _get_welcome_uri(self) -> str | None:
        sp_client = getattr(self, "sp", None)
        if not sp_client or not hasattr(sp_client, "album_tracks") or not hasattr(sp_client, "album"):
            return None

        try:
            welcome_tracks = self.get_spotify_daily_drive_welcome_tracks()
            if not welcome_tracks:
                return None

            # datetime.weekday(): Monday=0 .. Sunday=6
            # The album ordering appears to be Sunday..Saturday so shift by +1
            weekday = datetime.now().weekday()
            welcome_index = (weekday + 1) % 7
            if 0 <= welcome_index < len(welcome_tracks):
                return welcome_tracks[welcome_index].uri
        except spotipy.SpotifyException:
            return None

        return None
