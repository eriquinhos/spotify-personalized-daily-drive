import spotipy

from daily_drive.models.episode import Episode
from daily_drive.models.playlist import Playlist
from daily_drive.models.podcast import Podcast
from daily_drive.models.track import Track
from services.playlist_service import PlaylistService


def _make_track(uri: str) -> Track:
    return Track(
        id="",
        name="",
        artists=[],
        album_id="",
        release_date="",
        uri=uri,
        url="",
    )


def _make_episode(podcast_id: str, uri: str) -> Episode:
    return Episode(
        id="",
        name="",
        podcast=Podcast(id=podcast_id, key=podcast_id, name=podcast_id),
        release_date="",
        uri=uri,
        url="",
    )


def test_build_structured_uris_basic():
    svc = PlaylistService(sp=None)
    tracks = [_make_track(f"t{i}") for i in range(1, 5)]
    episodes_by_podcast = {
        svc.PODCAST_ORDER[0]: [
            _make_episode(svc.PODCAST_ORDER[0], "e1"),
        ],
        svc.PODCAST_ORDER[1]: [
            _make_episode(svc.PODCAST_ORDER[1], "e2"),
        ],
    }

    uris = svc._build_structured_uris(tracks, [], episodes_by_podcast)  # noqa: SLF001
    expected = ["t1", "e1", "t2", "t3", "e2", "t4"]
    assert uris == expected


def test_build_structured_uris_no_episodes():
    svc = PlaylistService(sp=None)
    tracks = [_make_track(f"t{i}") for i in range(1, 4)]
    uris = svc._build_structured_uris(tracks, [], {})  # noqa: SLF001
    assert uris == ["t1", "t2", "t3"]


def test_build_structured_uris_no_tracks_with_episodes():
    svc = PlaylistService(sp=None)
    tracks = []
    episodes_by_podcast = {
        svc.PODCAST_ORDER[0]: [
            Episode(
                id="e1",
                name="",
                podcast=Podcast(
                    id=svc.PODCAST_ORDER[0],
                    key="k",
                    name="n",
                ),
                release_date="",
                uri="e1",
                url="",
            )
        ],
        svc.PODCAST_ORDER[1]: [
            Episode(
                id="e2",
                name="",
                podcast=Podcast(
                    id=svc.PODCAST_ORDER[1],
                    key="k2",
                    name="n2",
                ),
                release_date="",
                uri="e2",
                url="",
            )
        ],
    }

    uris = svc._build_structured_uris(tracks, [], episodes_by_podcast)  # noqa: SLF001
    assert uris[0] == "e1"
    assert "e2" in uris


class DummySP:
    def __init__(self):
        self.added = []

    def playlist_add_items(self, playlist_id: str, uris: list) -> None:
        self.added.append((playlist_id, tuple(uris)))

    def playlist_replace_items(self, playlist_id: str, items: list) -> None:
        return None

    def playlist(self, playlist_id: str) -> dict:
        return {
            "id": playlist_id,
            "name": "Personal Daily Drive",
            "public": True,
            "uri": f"uri:{playlist_id}",
            "external_urls": {"spotify": "u"},
        }


def test_add_tracks_and_episodes_success():
    sp = DummySP()
    svc = PlaylistService(sp)
    playlist = Playlist(
        id="pl1",
        name="My PL",
        tracks=[],
        owner=None,
        public=True,
        uri="uri:pl1",
        url="",
    )
    tracks = [
        Track(
            id="t1",
            name="",
            artists=[],
            album_id="",
            release_date="",
            uri="uri:t1",
            url="",
        )
    ]
    episodes = [
        Episode(
            id="e1",
            name="",
            podcast=Podcast(
                id="p1",
                key="p1",
                name="p1",
            ),
            release_date="",
            uri="uri:e1",
            url="",
        )
    ]

    res_t = svc.add_tracks_to_playlist(playlist, tracks)
    assert "Added 1 tracks" in res_t

    res_e = svc.add_episodes_to_playlist(playlist, episodes)
    assert "Added 1 episodes" in res_e


def test_add_image_file_not_found() -> None:
    sp = DummySP()
    svc = PlaylistService(sp)
    msg = svc._add_image_to_playlist("pl1", "nonexistent_file.jpg")  # noqa: SLF001
    assert "not found" in msg


def test_refresh_existing_playlist_and_create_flow(monkeypatch: object) -> None:
    sp = DummySP()
    svc = PlaylistService(sp)

    monkeypatch.setattr(
        PlaylistService, "_add_image_to_playlist", lambda self, pid, p: "ok"
    )
    monkeypatch.setattr(
        PlaylistService,
        "_add_structured_content_to_playlist",
        lambda self, playlist, tracks, episodes: "structured ok",
    )

    tracks = []
    episodes = []
    result = svc._refresh_existing_playlist("pl1", tracks, episodes)  # noqa: SLF001
    assert result == "structured ok"

    class DummyUserService:
        def get_user_info(self) -> object:
            return type("U", (), {"id": "u1"})

        def get_user_playlists(self, limit: int = 100) -> list:
            return [type("P", (), {"name": "Personal Daily Drive", "id": "pl1"})]

    svc.user_service = DummyUserService()
    monkeypatch.setattr(
        PlaylistService,
        "_refresh_existing_playlist",
        lambda self, pid, t, e: "refreshed",
    )
    out = svc.create_daily_drive_playlist([], [])
    assert out == "refreshed"


def test_add_image_upload_success(monkeypatch: object, tmp_path: object) -> None:
    img = tmp_path / "img.jpg"
    img.write_bytes(b"binarydata")

    class SP:
        def __init__(self):
            self.uploaded = None

        def playlist_upload_cover_image(self, playlist_id: str, img_b64: str) -> None:
            self.uploaded = (playlist_id, img_b64)

    sp = SP()
    svc = PlaylistService(sp)
    res = svc._add_image_to_playlist("pl1", str(img))  # noqa: SLF001
    assert "uploaded successfully" in res
    assert sp.uploaded is not None


def test_add_structured_content_to_playlist_calls_sp(monkeypatch: object) -> None:
    class SP:
        def __init__(self) -> None:
            self.added = None

        def playlist_add_items(self, playlist_id: str, uris: list) -> None:
            self.added = (playlist_id, tuple(uris))

    sp = SP()
    svc = PlaylistService(sp)
    playlist = Playlist(
        id="plx",
        name="X",
        tracks=[],
        owner=None,
        public=True,
        uri="",
        url="",
    )
    tracks = [
        Track(
            id="t1",
            name="",
            artists=[],
            album_id="",
            release_date="",
            uri="t1",
            url="",
        ),
        Track(
            id="t2",
            name="",
            artists=[],
            album_id="",
            release_date="",
            uri="t2",
            url="",
        ),
    ]
    episodes = [
        Episode(
            id="e1",
            name="",
            podcast=Podcast(
                id=svc.PODCAST_ORDER[0],
                key="k",
                name="n",
            ),
            release_date="",
            uri="e1",
            url="",
        )
    ]
    res = svc._add_structured_content_to_playlist(playlist, tracks, episodes)  # noqa: SLF001
    assert "Added" in res
    assert sp.added is not None


def test_create_daily_drive_playlist_new(monkeypatch: object) -> None:
    class SP:
        def user_playlist_create(self, user_id: str, name: str, *, public: bool = True) -> dict:
            return {
                "id": "newid",
                "name": name,
                "public": True,
                "uri": "uri:newid",
                "external_urls": {"spotify": "u"},
            }

    sp = SP()
    svc = PlaylistService(sp)

    class DummyUserService:
        def get_user_info(self) -> object:
            return type("U", (), {"id": "u1"})

        def get_user_playlists(self, limit: int = 100) -> list:
            return []

    svc.user_service = DummyUserService()
    monkeypatch.setattr(
        PlaylistService, "_add_image_to_playlist", lambda self, pid, p: "ok"
    )
    monkeypatch.setattr(
        PlaylistService,
        "_add_structured_content_to_playlist",
        lambda self, playlist, tracks, episodes: "ok",
    )

    out = svc.create_daily_drive_playlist([], [])
    assert "created successfully" in out


def test_add_tracks_raises_spotify_exception() -> None:
    class SP:
        def playlist_add_items(self, playlist_id: str, uris: list) -> None:
            raise spotipy.SpotifyException(400, -1, "bad")

    svc = PlaylistService(SP())
    pl = Playlist(
        id="p",
        name="n",
        tracks=[],
        owner=None,
        public=True,
        uri="",
        url="",
    )
    t = [
        Track(
            id="t1",
            name="",
            artists=[],
            album_id="",
            release_date="",
            uri="u1",
            url="",
        )
    ]
    res = svc.add_tracks_to_playlist(pl, t)
    assert res.startswith("Error adding tracks to playlist")


def test_add_episodes_raises_spotify_exception() -> None:
    class SP:
        def playlist_add_items(self, playlist_id: str, uris: list) -> None:
            raise spotipy.SpotifyException(500, -1, "err")

    svc = PlaylistService(SP())
    pl = Playlist(
        id="p",
        name="n",
        tracks=[],
        owner=None,
        public=True,
        uri="",
        url="",
    )
    e = [
        Episode(
            id="e1",
            name="",
            podcast=Podcast(id="p1", key="k", name="n"),
            release_date="",
            uri="u1",
            url="",
        )
    ]
    res = svc.add_episodes_to_playlist(pl, e)
    assert res.startswith("Error adding episodes to playlist")


def test_add_image_raises_spotify_exception(tmp_path: object) -> None:
    img = tmp_path / "i.jpg"
    img.write_bytes(b"x")

    class SP:
        def playlist_upload_cover_image(self, pid: str, data: str) -> None:
            raise spotipy.SpotifyException(403, -1, "forbidden")

    svc = PlaylistService(SP())
    res = svc._add_image_to_playlist("p", str(img))  # noqa: SLF001
    assert res.startswith("Error uploading image to playlist")


def test_add_structured_content_handles_spotify_exception() -> None:
    class SP:
        def playlist_add_items(self, playlist_id: str, uris: list) -> None:
            raise spotipy.SpotifyException(400, -1, "bad")

    svc = PlaylistService(SP())
    pl = Playlist(
        id="plx",
        name="X",
        tracks=[],
        owner=None,
        public=True,
        uri="",
        url="",
    )
    res = svc._add_structured_content_to_playlist(pl, [], [])  # noqa: SLF001
    assert res.startswith("Error adding content to playlist")


def test_create_daily_drive_playlist_handles_spotify_exception(monkeypatch: object) -> None:
    class SP:
        def user_playlist_create(self, user_id: str, name: str, *, public: bool = True) -> None:
            raise spotipy.SpotifyException(500, -1, "nope")

    sp = SP()
    svc = PlaylistService(sp)

    class DummyUserService:
        def get_user_info(self) -> object:
            return type("U", (), {"id": "u1"})

        def get_user_playlists(self, limit: int = 100) -> list:
            return []

    svc.user_service = DummyUserService()
    out = svc.create_daily_drive_playlist([], [])
    assert out.startswith("Error creating playlist")


def test_refresh_existing_playlist_handles_spotify_exception() -> None:
    class SP:
        def playlist_replace_items(self, playlist_id: str, items: list) -> None:
            import spotipy

            raise spotipy.SpotifyException(400, -1, "bad")

    svc = PlaylistService(SP())
    out = svc._refresh_existing_playlist("pl1", [], [])  # noqa: SLF001
    assert out.startswith("Error refreshing playlist")
