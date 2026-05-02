import spotipy

from utils.formatter import normalize, similarity


class PodcastService:
    CAFE_DA_MANHA_ID = "6WRTzGhq3uFxMrxHrHh1lo"
    O_ASSUNTO_ID = "4gkKyFdZzkv1eDnlTVrguk"
    RESUMAO_DIARIO_ID = "7fzhxpt0RgWaLFYydsv2b4"
    BOLETIM_FOLHA_ID = "45PqwRAJBEOdNc28ijJnIz"
    NOTICIA_NO_SEU_TEMPO_ID = "3M3xXhNXudIXGNSrjvoETG"
    PANORAMA_CBN_ID = "3mKy8vUlAHoLxZVaILsUWw"
    SEGUNDOS_123_ID = "4Z5CoK9UJq3ykgLbcBTQwP"

    def __init__(self, sp: spotipy.Spotify) -> None:
        self.sp = sp

    def _get_best_podcast(self, podcasts: list[tuple[str, list[str], list[str]]],
                          name: str,
                          publishers: list[str]) -> str | None:
        scored = []
        name_norm = normalize(name)

        for podcast in podcasts:
            name_resulted = podcast.get("name", "")
            publisher_resulted = podcast.get("publisher", "")

        score = similarity(name, name_resulted) * 100

        if normalize(name_resulted) == name_norm:
            score += 50
        elif name_norm in normalize(name_resulted):
            score += 20

        if publishers:
            for pub in publishers:
                if normalize(pub) in normalize(publisher_resulted):
                    score += 25

        scored.append((score, podcast))

        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_podcast = scored[0]

        if best_score < 70:
            return None

        return best_podcast

    def _get_podcast_episodes(self, podcast_id: str, limit: int = 5) -> list:
        episodes = self.sp.show_episodes(podcast_id, limit=limit)
        return episodes["items"]

    def get_user_top_podcasts(self, time_range: str = "short_term", limit: int = 20) -> list:
        # Not used for my personal daily drive playlist, but could be useful if you want to use your own top podcasts
        # instead of the predefined ones
        top_podcasts = self.sp.current_user_top_shows(
            time_range=time_range, limit=limit)
        return top_podcasts["items"]

    def find_podcast_by_name(self, name: str, publishers: list[str], market: str = "BR") -> dict | None:
        # Used to find the podcast IDs for the predefined podcasts, not used in the main flow
        search = self.sp.search(
            q=f'"{name}"',
            type="show",
            limit=10,
            market=market
        )

        podcasts = search.get("shows", {}).get("items", [])
        if not podcasts:
            return None

        return self._get_best_podcast(podcasts, name, publishers)

    def get_last_podcast_episode(self, podcast_id: str, limit: int = 5) -> dict | None:
        episodes = self._get_podcast_episodes(podcast_id, limit)
        return episodes[0] if episodes else None
