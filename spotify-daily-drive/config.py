import os
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

SCOPE = "user-library-read playlist-modify-private playlist-read-private user-read-playback-position user-top-read user-read-recently-played"

MAX_PLAYLIST_LENGTH = 60 * 60 * 1000  # 1 hour in milliseconds

