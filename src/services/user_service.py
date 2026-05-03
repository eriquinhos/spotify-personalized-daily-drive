
import spotipy

from daily_drive.models.album import Album
from daily_drive.models.artist import Artist
from daily_drive.models.playlist import Playlist
from daily_drive.models.track import Track
from daily_drive.models.user import User


class UserService:
    def __init__(self, sp: spotipy.Spotify) -> None:
        self.sp = sp

    def _map_user(self, user: dict) -> User:
        return User(
            id=user.get("id", ""),
            name=user.get("display_name") or user.get("id", ""),
            email=user.get("email"),
            uri=user.get("uri", ""),
            url=user.get("external_urls", {}).get("spotify", ""),
            images=[img.get("url") for img in user.get("images", [])] or None,
        )

    def _map_artist(self, artist: dict) -> Artist:
        return Artist(
            id=artist.get("id", ""),
            name=artist.get("name", ""),
            uri=artist.get("uri", ""),
            url=artist.get("external_urls", {}).get("spotify", ""),
        )

    def _map_album(self, album: dict) -> Album:
        if not album:
            return Album(
                id="",
                name="",
                artists=[],
                release_date="",
                tracks=[],
                total_tracks=None,
                uri="",
                url="",
            )

        artists = [self._map_artist(a) for a in album.get("artists", [])]
        return Album(
            id=album.get("id", ""),
            name=album.get("name", ""),
            artists=artists,
            release_date=album.get("release_date", ""),
            tracks=[],
            total_tracks=album.get("total_tracks"),
            uri=album.get("uri", ""),
            url=album.get("external_urls", {}).get("spotify", ""),
        )

    def _map_track(self, track: dict) -> Track:
        artists = [self._map_artist(a) for a in track.get("artists", [])]
        alb = self._map_album(track.get("album", {}) or {})
        return Track(
            id=track.get("id", ""),
            name=track.get("name", ""),
            artists=artists,
            album_id=alb.id,
            release_date=alb.release_date or track.get("release_date", ""),
            uri=track.get("uri", ""),
            url=track.get("external_urls", {}).get("spotify", ""),
            explicit=track.get("explicit", False),
            duration_ms=track.get("duration_ms"),
        )

    def _map_playlist(self, playlist: dict) -> Playlist:
        return Playlist(
            id=playlist.get("id", ""),
            name=playlist.get("name", ""),
            tracks=[],
            owner=self._map_user(playlist.get("owner", {})),
            public=playlist.get("public", False),
            uri=playlist.get("uri", ""),
            url=playlist.get("external_urls", {}).get("spotify", ""),
        )

    def get_user_info(self) -> User:
        return self._map_user(self.sp.current_user())

    def get_user_top_tracks(self, time_range: str = "short_term", limit: int = 20) -> list[Track]:
        response = self.sp.current_user_top_tracks(
            time_range=time_range, limit=limit)
        items = response.get("items", []) if response else []
        return [self._map_track(t) for t in items]

    def get_user_top_artists(self, time_range: str = "short_term", limit: int = 20) -> list[Artist]:
        response = self.sp.current_user_top_artists(
            time_range=time_range, limit=limit)
        items = response.get("items", []) if response else []
        return [self._map_artist(a) for a in items]

    def get_user_playlists(self, limit: int = 100) -> list[Playlist]:
        response = self.sp.current_user_playlists(limit=limit)
        items = response.get("items", []) if response else []
        return [self._map_playlist(p) for p in items]
