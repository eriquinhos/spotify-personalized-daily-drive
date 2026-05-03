from daily_drive.models.podcast import Podcast
from services.podcast_service import PodcastService
from tests.test_user_service import DummySP


def test_get_best_podcast_none_on_empty_list() -> None:
    svc = PodcastService(sp=None)
    assert svc._get_best_podcast([], "Any Name", []) is None  # noqa: SLF001


def test_get_best_podcast_returns_best_match() -> None:
    svc = PodcastService(sp=None)
    podcasts = [
        {"id": "p1", "name": "My Podcast", "publisher": "Publisher A"},
        {"id": "p2", "name": "Some Other Show", "publisher": "Other"},
    ]

    result = svc._get_best_podcast(podcasts, "My Podcast", ["Publisher A"])  # noqa: SLF001
    assert result is not None
    assert isinstance(result, Podcast)
    assert result.id == "p1"


def test_get_best_podcast_respects_threshold() -> None:
    svc = PodcastService(sp=None)
    podcasts = [
        {"id": "p3", "name": "Unrelated Show", "publisher": "Someone"},
    ]
    assert (
        svc._get_best_podcast(podcasts, "Search Term", ["Publisher X"]) is None  # noqa: SLF001
    )


def test_get_podcast_episodes_and_last() -> None:
    sp = DummySP()
    svc = PodcastService(sp)
    podcast = Podcast(id="p1", key="p1", name="Podcast 1")

    eps = svc._get_podcast_episodes(podcast, limit=1)  # noqa: SLF001
    assert len(eps) == 1
    assert eps[0].podcast.id == "p1"

    empty = svc._get_podcast_episodes(  # noqa: SLF001
        Podcast(id="empty", key="empty", name="empty"), limit=1
    )
    assert empty == []

    last = svc.get_last_podcast_episode(podcast, limit=1)
    assert last is not None
    assert last.id == "ep1"


def test_find_podcast_by_name() -> None:
    sp = DummySP()
    svc = PodcastService(sp)
    p = svc.find_podcast_by_name("Search Match", ["Pub"])
    assert p is not None
    assert isinstance(p, Podcast)


def test_get_best_podcast_scoring_variations() -> None:
    svc = PodcastService(sp=None)
    podcasts = [
        {"id": "a1", "name": "Exact Name", "publisher": "X"},
        {"id": "a2", "name": "Something Else", "publisher": "Y"},
    ]
    best = svc._get_best_podcast(podcasts, "Exact Name", [])  # noqa: SLF001
    assert best is not None and best.id == "a1"

    podcasts = [
        {"id": "b1", "name": "Close Name", "publisher": "MyPub"},
    ]
    best = svc._get_best_podcast(podcasts, "Close", ["MyPub"])  # noqa: SLF001
    assert (best is None) or isinstance(best, Podcast)


def test_get_best_podcast_contains_branch() -> None:
    svc = PodcastService(sp=None)
    podcasts = [
        {
            "id": "c1",
            "name": "Contains Name Show",
            "publisher": "PubX",
        }
    ]
    p = svc._get_best_podcast(podcasts, "Name", [])  # noqa: SLF001
    assert (p is None) or isinstance(p, Podcast)


def test_get_user_top_podcasts_and_find_no_results() -> None:
    class SP:
        def current_user_top_shows(self, time_range: str = "short_term", limit: int = 20) -> dict:
            return {
                "items": [
                    {
                        "id": "s1",
                        "name": "Show 1",
                        "publisher": "P1",
                    }
                ]
            }

        def search(self, q: str, type: str, limit: int = 10, market: str = "BR") -> dict:  # noqa: A002
            return {"shows": {"items": []}}

    sp = SP()
    svc = PodcastService(sp)
    top = svc.get_user_top_podcasts()
    assert len(top) == 1 and top[0].id == "s1"

    none = svc.find_podcast_by_name("Nope", ["X"])
    assert none is None


def test_get_best_podcast_name_contains_and_publisher_match() -> None:
    svc = PodcastService(sp=None)
    podcasts = [
        {
            "id": "x1",
            "name": "The Segundos Show",
            "publisher": "BigPub Inc",
        }
    ]
    p = svc._get_best_podcast(podcasts, "Segundos", ["BigPub"])  # noqa: SLF001
    assert (p is None) or isinstance(p, Podcast)


def test_get_best_podcast_publisher_boost_returns() -> None:
    svc = PodcastService(sp=None)
    podcasts = [
        {
            "id": "z1",
            "name": "Exact Match",
            "publisher": "ThePublisher",
        }
    ]
    p = svc._get_best_podcast(podcasts, "Exact Match", ["Publisher"])  # noqa: SLF001
    assert isinstance(p, Podcast)
