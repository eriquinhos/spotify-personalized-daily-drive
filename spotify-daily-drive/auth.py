import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, SCOPE

def get_spotify_client():
    """
    Create and return an authenticated Spotify client.
    
    Returns:
        spotipy.Spotify: An authenticated Spotify client.
    """
    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE
    )
    return spotipy.Spotify(auth_manager=auth_manager)

def is_authenticated(sp):
    """
    Check if the Spotify client is authenticated.
    
    Args:
        sp (spotipy.Spotify): Spotify client to check.
    
    Returns:
        bool: True if authenticated, False otherwise.
    """
    try:
        sp.current_user()
        return True
    except:
        return False

