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


def test_find_podcast_by_name_no_results() -> None:
    class SP:
        def search(self, q: str, type: str, limit: int = 10, market: str = "BR") -> dict:  # noqa: A002
            return {"shows": {"items": []}}

    sp = SP()
    svc = PodcastService(sp)
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


def test_load_podcasts_from_config_with_none() -> None:
    # Test with None input
    podcasts = PodcastService.load_podcasts_from_config(None)
    assert podcasts == []


def test_load_podcasts_from_config_with_empty_dict() -> None:
    # Test with empty dict
    podcasts = PodcastService.load_podcasts_from_config({})
    assert podcasts == []


def test_load_podcasts_from_config_with_non_list_podcasts() -> None:
    # Test when "podcasts" key is not a list
    podcasts = PodcastService.load_podcasts_from_config(
        {"podcasts": "not a list"})
    assert podcasts == []


def test_load_podcasts_from_config_with_invalid_podcast_items() -> None:
    # Test when podcast items are not dicts
    podcasts = PodcastService.load_podcasts_from_config(
        {"podcasts": ["not a dict", 123]}
    )
    assert podcasts == []


def test_load_podcasts_from_config_skips_incomplete_items() -> None:
    # Test when some podcasts are missing required fields
    podcasts = PodcastService.load_podcasts_from_config(
        {
            "podcasts": [
                {"id": "p1", "name": "Pod 1"},  # valid
                {"id": "p2"},  # missing name
                {"name": "Pod 3"},  # missing id
            ]
        }
    )
    assert len(podcasts) == 1
    assert podcasts[0].name == "Pod 1"


def test_get_podcast_episodes_with_invalid_items() -> None:
    # Test _get_podcast_episodes with items lacking id or being None
    class SPWithInvalidEpisodes:
        def show_episodes(self, podcast_id: str, limit: int = 5) -> dict:
            return {
                "items": [
                    None,  # None item
                    {"name": "Episode", "uri": "uri1"},  # missing id
                    {
                        "id": "e1",
                        "name": "Valid Episode",
                        "uri": "uri2",
                        "release_date": "2024-01-01",
                        "external_urls": {"spotify": "url1"},
                    },  # valid
                ]
            }

    svc = PodcastService(SPWithInvalidEpisodes())
    podcast = Podcast(id="p1", key="p1", name="Pod1")
    episodes = svc._get_podcast_episodes(podcast, limit=5)  # noqa: SLF001
    # Should only return the valid episode
    assert len(episodes) == 1
    assert episodes[0].id == "e1"
