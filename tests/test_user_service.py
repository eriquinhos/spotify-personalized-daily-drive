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

    def current_user_top_tracks(self, time_range: str = "short_term", limit: int = 20) -> dict:
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

    def current_user_top_artists(self, time_range: str = "short_term", limit: int = 20) -> dict:
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


def test_map_album_empty() -> None:
    sp = DummySP()
    svc = UserService(sp)
    alb = svc._map_album({})  # noqa: SLF001
    assert alb.id == ""
    assert alb.tracks == []
