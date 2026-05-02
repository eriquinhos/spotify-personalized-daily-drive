
import spotipy


class PlaylistService:
    def __init__(self, sp: spotipy.Spotify) -> None:
        self.sp = sp

    def create_playlist(self, user_id: str, name: str, description: str = "", public: bool = False) -> str:
        pass