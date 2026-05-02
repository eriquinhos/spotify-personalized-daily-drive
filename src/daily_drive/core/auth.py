import spotipy
from spotipy.oauth2 import SpotifyOAuth


class Auth:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scope: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope

    def authenticate(self) -> spotipy.Spotify:
        sp_oauth = SpotifyOAuth(client_id=self.client_id,
                                client_secret=self.client_secret,
                                redirect_uri=self.redirect_uri,
                                scope=self.scope)

        token_info = sp_oauth.get_access_token()
        access_token = token_info["access_token"]
        return spotipy.Spotify(auth=access_token)

    def refresh_token(self, sp_oauth: SpotifyOAuth) -> str:
        token_info = sp_oauth.refresh_access_token(sp_oauth.cache_handler.get_cached_token()["refresh_token"])
        return token_info["access_token"]

