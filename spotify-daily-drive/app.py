import streamlit as st
from auth import get_spotify_client, is_authenticated
from playlist_manager import PlaylistManager
from scheduler import setup_scheduler
from logger import logger
import datetime

def set_theme(theme):
    """Set the app theme (light or dark)."""
    st.session_state.theme = theme
    st.experimental_set_query_params(theme=theme)

def main():
    st.set_page_config(page_title="Spotify Daily Drive", page_icon=":musical_note:", layout="wide")
    
    # Theme handling
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    # Apply theme
    if st.session_state.theme == 'dark':
        st.markdown("""
        <style>
        .stApp {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.title("Spotify Daily Drive")

    # Theme toggle
    theme = st.sidebar.radio("Theme", ('Light', 'Dark'))
    if theme == 'Light' and st.session_state.theme != 'light':
        set_theme('light')
    elif theme == 'Dark' and st.session_state.theme != 'dark':
        set_theme('dark')

    # Initialize session state
    if 'spotify_client' not in st.session_state:
        st.session_state.spotify_client = get_spotify_client()

    if not is_authenticated(st.session_state.spotify_client):
        st.warning("Please log in to Spotify to use this app.")
        auth_url = st.session_state.spotify_client.auth_manager.get_authorize_url()
        st.markdown(f"[Login to Spotify]({auth_url})")
    else:
        try:
            playlist_manager = PlaylistManager(st.session_state.spotify_client)

            # Set up the scheduler
            scheduler = setup_scheduler(st.session_state.spotify_client)

            st.success("Successfully connected to Spotify!")

            # Sidebar for playlist customization
            st.sidebar.header("Customize Your Daily Drive")
            music_ratio = st.sidebar.slider("Music to Podcast Ratio", 0.0, 1.0, 0.7, 0.1)
            
            excluded_artists = st.sidebar.text_input("Exclude Artists (comma-separated)")
            excluded_genres = st.sidebar.text_input("Exclude Genres (comma-separated)")
            
            st.sidebar.subheader("Preferred Time Ranges")
            music_start = st.sidebar.time_input("Music Start Time", datetime.time(9, 0))
            music_end = st.sidebar.time_input("Music End Time", datetime.time(18, 0))
            podcast_start = st.sidebar.time_input("Podcast Start Time", datetime.time(7, 0))
            podcast_end = st.sidebar.time_input("Podcast End Time", datetime.time(22, 0))

            if st.sidebar.button("Update Daily Drive"):
                with st.spinner("Updating your Daily Drive playlist..."):
                    playlist_manager.update_daily_drive(
                        music_ratio,
                        excluded_artists.split(',') if excluded_artists else None,
                        excluded_genres.split(',') if excluded_genres else None,
                        (music_start, music_end),
                        (podcast_start, podcast_end)
                    )
                st.success("Daily Drive playlist updated successfully!")

            # Main content area
            col1, col2 = st.columns(2)

            with col1:
                st.header("Current Daily Drive Playlist")
                playlist_items = playlist_manager.get_current_playlist()
                for item in playlist_items['items']:
                    track = item['track']
                    if track['type'] == 'track':
                        st.write(f"🎵 {track['name']} - {track['artists'][0]['name']}")
                    elif track['type'] == 'episode':
                        st.write(f"🎙️ {track['name']} - {track['show']['name']}")

            with col2:
                st.header("Listening Stats")
                stats = playlist_manager.get_listening_stats()
                
                st.subheader("Top Tracks")
                for i, track in enumerate(stats['top_tracks'], 1):
                    st.write(f"{i}. {track['name']} - {track['artist']}")
                
                st.subheader("Top Artists")
                for i, artist in enumerate(stats['top_artists'], 1):
                    st.write(f"{i}. {artist}")
                
                st.subheader("History")
                st.write(f"Total tracks in history: {stats['total_tracks_in_history']}")
                st.write(f"Total episodes in history: {stats['total_episodes_in_history']}")

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            st.error(f"An error occurred. Please try again later or contact support.")

if __name__ == "__main__":
    main()

