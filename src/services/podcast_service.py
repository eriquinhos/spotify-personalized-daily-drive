import spotipy

from daily_drive.models.episode import Episode
from daily_drive.models.podcast import Podcast
from utils.formatter import normalize, similarity


class PodcastService:
    def __init__(self, sp: spotipy.Spotify) -> None:
        self.sp = sp

    def _get_best_podcast(
        self,
        podcasts: list[dict],
        name: str,
        publishers: list[str],
    ) -> Podcast | None:
        scored = []
        name_norm = normalize(name)

        for p in podcasts:
            name_resulted = p.get("name", "")
            publisher_resulted = p.get("publisher", "")

            score = similarity(name, name_resulted) * 100

            if normalize(name_resulted) == name_norm:
                score += 50
            elif name_norm in normalize(name_resulted):
                score += 20

            for pub in publishers:
                if normalize(pub) in normalize(publisher_resulted):
                    score += 25

            scored.append((score, p))

        if not scored:
            return None

        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_podcast = scored[0]

        if best_score < 70:
            return None

        return Podcast(
            id=best_podcast["id"],
            key=best_podcast["name"],
            name=best_podcast["name"],
            publisher=best_podcast.get("publisher"),
        )

    def _get_podcast_episodes(self, podcast: Podcast, limit: int = 5) -> list[Episode]:
        search = self.sp.show_episodes(podcast.id, limit=limit)
        items = search.get("items", [])

        if not items:
            return []

        return [
            Episode(
                id=ep["id"],
                name=ep["name"],
                podcast=podcast,
                release_date=ep.get("release_date", ""),
                uri=ep.get("uri", ""),
                url=ep.get("external_urls", {}).get("spotify", ""),
            )
            for ep in items
        ]

    def get_user_top_podcasts(self, time_range: str = "short_term", limit: int = 20) -> list[Podcast]:
        top_podcasts = self.sp.current_user_top_shows(
            time_range=time_range, limit=limit)
        items = top_podcasts.get("items", [])
        return [
            Podcast(
                id=item["id"],
                key=item["name"],
                name=item["name"],
                publisher=item.get("publisher"),
            )
            for item in items
        ]

    def find_podcast_by_name(self, name: str, publishers: list[str], market: str = "BR") -> Podcast | None:
        search = self.sp.search(
            q=f'"{name}"', type="show", limit=10, market=market)
        podcasts = search.get("shows", {}).get("items", [])
        if not podcasts:
            return None

        return self._get_best_podcast(podcasts, name, publishers)

    def get_last_podcast_episode(self, podcast: Podcast, limit: int = 5) -> Episode | None:
        episodes = self._get_podcast_episodes(podcast, limit)
        return episodes[0] if episodes else None
