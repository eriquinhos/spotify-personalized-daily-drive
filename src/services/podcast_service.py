import spotipy

from daily_drive.models.episode import Episode
from daily_drive.models.podcast import Podcast
from utils.formatter import normalize, similarity


class PodcastService:
    def __init__(self, sp: spotipy.Spotify) -> None:
        self.sp = sp

    @staticmethod
    def load_podcasts_from_config(yaml_config: dict | None = None) -> list[Podcast]:
        """Load podcasts from a YAML config dict.

        Returns an empty list when the YAML is missing or invalid. Consumers
        may decide to fall back to user-top podcasts when no config is provided.
        """
        raw_podcasts = None
        if isinstance(yaml_config, dict):
            raw_podcasts = yaml_config.get(
                "podcasts") if "podcasts" in yaml_config else None

        if not isinstance(raw_podcasts, list) or not raw_podcasts:
            return []

        podcasts: list[Podcast] = []
        for raw_podcast in raw_podcasts:
            if not isinstance(raw_podcast, dict):
                continue

            podcast_id = str(raw_podcast.get("id", "")).strip()
            podcast_name = str(raw_podcast.get("name", "")).strip()
            podcast_key = str(raw_podcast.get(
                "key", podcast_id or podcast_name)).strip()
            if not podcast_id or not podcast_name:
                continue

            podcasts.append(
                Podcast(
                    id=podcast_id,
                    key=podcast_key,
                    name=podcast_name,
                    publisher=raw_podcast.get("publisher"),
                )
            )

        return podcasts

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
        items = search.get("items", []) or []

        if not items:
            return []

        episodes: list[Episode] = []
        for ep in items:
            if not ep or not isinstance(ep, dict):
                continue
            ep_id = ep.get("id")
            if not ep_id:
                continue

            episodes.append(
                Episode(
                    id=ep_id,
                    name=ep.get("name", ""),
                    podcast=podcast,
                    release_date=ep.get("release_date", ""),
                    uri=ep.get("uri", ""),
                    url=ep.get("external_urls", {}).get("spotify", ""),
                )
            )

        return episodes

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
