from services.user_service import UserService


class DummySP:
    def __init__(self):
        self._user = {
            "id": "u1",
            "display_name": "User One",
            "email": "u1@example.com",
            "uri": "spotify:user:u1",
            "external_urls": {"spotify": "https://open.spotify.com/user/u1"},
            "images": [{"url": "https://img"}],
        }

    def current_user(self):
        return self._user

    def current_user_top_tracks(
        self,
        time_range: str = "short_term",
        offset: int = 0,
        limit: int = 20,
    ) -> dict:
        return {
            "items": [
                {
                    "id": "t1",
                    "name": "Track 1",
                    "artists": [],
                    "album": {"id": "a1", "name": "Album 1", "artists": []},
                    "uri": "uri:t1",
                    "external_urls": {"spotify": "u"},
                }
            ]
        }

    def current_user_top_artists(
        self,
        time_range: str = "short_term",
        offset: int = 0,
        limit: int = 20,
    ) -> dict:
        return {
            "items": [
                {
                    "id": "ar1",
                    "name": "Artist 1",
                    "uri": "uri:ar1",
                    "external_urls": {"spotify": "u"},
                }
            ]
        }

    def current_user_playlists(self, limit: int = 100) -> dict:
        return {
            "items": [
                {
                    "id": "p1",
                    "name": "My Playlist",
                    "owner": self._user,
                    "public": False,
                    "uri": "uri:p1",
                    "external_urls": {"spotify": "u"},
                }
            ]
        }

    def show_episodes(self, podcast_id: str, limit: int = 5) -> dict:
        if podcast_id == "empty":
            return {"items": []}
        return {
            "items": [
                {
                    "id": "ep1",
                    "name": "Episode 1",
                    "release_date": "2020-01-01",
                    "uri": "uri:ep1",
                    "external_urls": {"spotify": "u"},
                }
            ]
        }

    def current_user_top_shows(self, time_range: str = "short_term", limit: int = 20) -> dict:
        return {
            "items": [
                {
                    "id": "s1",
                    "name": "Show 1",
                    "publisher": "Publisher 1",
                }
            ]
        }

    def search(self, q: str, type: str, limit: int = 10, market: str = "BR") -> dict:  # noqa: A002
        return {
            "shows": {
                "items": [
                    {"id": "s1", "name": "Search Match", "publisher": "Pub"}
                ]
            }
        }


def test_map_user_and_top_collections() -> None:
    sp = DummySP()
    svc = UserService(sp)

    user = svc.get_user_info()
    assert user.id == "u1"
    assert user.name == "User One"

    tracks = svc.get_user_top_tracks()
    assert len(tracks) == 1
    assert tracks[0].uri == "uri:t1"

    artists = svc.get_user_top_artists()
    assert len(artists) == 1
    assert artists[0].id == "ar1"

    playlists = svc.get_user_playlists()
    assert len(playlists) == 1
    assert playlists[0].name == "My Playlist"

    podcasts = svc.get_user_top_podcasts()
    assert len(podcasts) == 1
    assert podcasts[0].id == "s1"


def test_map_album_empty() -> None:
    sp = DummySP()
    svc = UserService(sp)
    alb = svc._map_album({})  # noqa: SLF001
    assert alb.id == ""
    assert alb.tracks == []


def test_is_track_available_with_none() -> None:
    sp = DummySP()
    svc = UserService(sp)
    # Should return True (fail-open) when track is None
    assert svc.is_track_available(None) is True


def test_is_track_available_with_empty_string() -> None:
    sp = DummySP()
    svc = UserService(sp)
    # Should return True (fail-open) when track is empty string
    assert svc.is_track_available("") is True


def test_is_track_available_with_object_missing_id() -> None:
    sp = DummySP()
    svc = UserService(sp)

    class FakeTrack:
        pass

    # Should return True (fail-open) when object has no id attribute
    assert svc.is_track_available(FakeTrack()) is True


def test_is_track_available_with_attribute_error() -> None:
    sp = DummySP()
    svc = UserService(sp)

    class BrokenTrack:
        @property
        def id(self) -> None:
            msg = "broken id property"
            raise AttributeError(msg)

    # Should return True (fail-open) when accessing id raises AttributeError
    assert svc.is_track_available(BrokenTrack()) is True


def test_is_track_available_with_sp_error() -> None:
    class SPWithError:
        def track(self, track_id: str) -> None:
            import spotipy

            raise spotipy.SpotifyException(400, -1, "error")

    svc = UserService(SPWithError())
    # Should return False when Spotify API returns error
    assert svc.is_track_available("t1") is False


def test_filter_available_tracks_with_broken_track() -> None:
    sp = DummySP()
    svc = UserService(sp)

    class BrokenTrack:
        def __getattribute__(self, name: str):
            msg = "broken"
            if name == "id":
                raise AttributeError(msg)
            return super().__getattribute__(name)

    # Should not crash and put broken track in available (fail-open)
    available, unavailable = svc.filter_available_tracks([BrokenTrack()])
    assert len(available) == 1
    assert len(unavailable) == 0


def test_filter_available_tracks_handles_exception_from_is_track_available() -> None:
    sp = DummySP()
    svc = UserService(sp)

    # Create a track that will cause is_track_available to raise an exception
    class ProblematicTrack:
        id = "t1"

    # Patch is_track_available to raise ValueError
    original_is_available = svc.is_track_available

    def broken_is_available(track: object) -> bool:
        msg = "problem"
        if isinstance(track, ProblematicTrack):
            raise TypeError(msg)
        return original_is_available(track)

    svc.is_track_available = broken_is_available

    # The filter should catch the exception and put the track in available (fail-open)
    available, unavailable = svc.filter_available_tracks([ProblematicTrack()])
    assert len(available) == 1
    assert len(unavailable) == 0


def test_is_track_available_raises_attribute_error_on_id_access() -> None:
    sp = DummySP()
    svc = UserService(sp)

    # Create a track where id property raises AttributeError
    class TrackWithBadId:
        @property
        def id(self) -> None:
            msg = "cannot access id"
            raise AttributeError(msg)

    # Should return True (fail-open) when accessing track.id raises AttributeError
    assert svc.is_track_available(TrackWithBadId()) is True


def test_is_track_available_with_available_markets_empty() -> None:
    # Test when track has empty available_markets list
    class SPWithMarkets:
        def track(self, track_id: str) -> dict:
            return {
                "id": "t1",
                "name": "Track",
                "available_markets": [],
                "is_playable": False,
            }

    svc = UserService(SPWithMarkets())
    # Should return False since is_playable is False
    assert svc.is_track_available("t1") is False


def test_is_track_available_with_available_markets_nonempty() -> None:
    # Test when track has non-empty available_markets list
    class SPWithMarkets:
        def track(self, track_id: str) -> dict:
            return {
                "id": "t1",
                "name": "Track",
                "available_markets": ["US", "BR"],
            }

    svc = UserService(SPWithMarkets())
    # Should return True since available_markets is non-empty
    assert svc.is_track_available("t1") is True


def test_is_track_available_with_unknown_track_format() -> None:
    # Test when track dict has no is_playable and no available_markets
    class SPWithUnknown:
        def track(self, track_id: str) -> dict:
            return {
                "id": "t1",
                "name": "Track",
            }

    svc = UserService(SPWithUnknown())
    # Should return True (fail-open assumption)
    assert svc.is_track_available("t1") is True
