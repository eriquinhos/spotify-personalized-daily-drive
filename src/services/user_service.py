
import spotipy


class UserService:
    def __init__(self, sp: spotipy.Spotify) -> None:
        self.sp = sp

    def get_user_id(self) -> str:
        user_info = self.sp.current_user()
        return user_info["id"]

    def get_user_top_tracks(self, time_range: str = "short_term", limit: int = 20) -> list:
        top_tracks = self.sp.current_user_top_tracks(time_range=time_range, limit=limit)
        return top_tracks["items"]