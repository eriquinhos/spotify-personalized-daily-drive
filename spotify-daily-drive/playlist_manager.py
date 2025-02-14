import random
from datetime import datetime, time
from config import MAX_PLAYLIST_LENGTH
from ml_recommender import MLRecommender
from logger import logger
import json
import os

class PlaylistManager:
    def __init__(self, sp):
        """
        Initialize the PlaylistManager.
        
        Args:
            sp (spotipy.Spotify): Authenticated Spotify client.
        """
        self.sp = sp
        self.user_id = sp.me()['id']
        self.daily_drive_playlist = self._get_or_create_daily_drive_playlist()
        self.ml_recommender = MLRecommender(sp)
        self.history = self._load_history()
        self.cache = {}

    def _get_or_create_daily_drive_playlist(self):
        """
        Get the existing Daily Drive playlist or create a new one if it doesn't exist.
        
        Returns:
            dict: Playlist object.
        """
        try:
            playlists = self.sp.user_playlists(self.user_id)
            for playlist in playlists['items']:
                if playlist['name'] == "Daily Drive":
                    return playlist
            
            return self.sp.user_playlist_create(self.user_id, "Daily Drive", public=False, description="Your personalized Daily Drive playlist")
        except Exception as e:
            logger.error(f"Error getting or creating Daily Drive playlist: {str(e)}")
            raise

    def _load_history(self):
        """Load playlist history from a file."""
        try:
            if os.path.exists('playlist_history.json'):
                with open('playlist_history.json', 'r') as f:
                    return json.load(f)
            return {'tracks': [], 'episodes': []}
        except Exception as e:
            logger.error(f"Error loading playlist history: {str(e)}")
            return {'tracks': [], 'episodes': []}

    def _save_history(self):
        """Save playlist history to a file."""
        try:
            with open('playlist_history.json', 'w') as f:
                json.dump(self.history, f)
        except Exception as e:
            logger.error(f"Error saving playlist history: {str(e)}")

    def update_daily_drive(self, music_ratio=0.7, excluded_artists=None, excluded_genres=None, music_time_range=None, podcast_time_range=None):
        """
        Update the Daily Drive playlist with new songs and podcasts.
        
        Args:
            music_ratio (float): Ratio of music to podcasts (0.7 means 70% music, 30% podcasts).
            excluded_artists (list): List of artist names to exclude.
            excluded_genres (list): List of genres to exclude.
            music_time_range (tuple): Preferred time range for music (start_time, end_time).
            podcast_time_range (tuple): Preferred time range for podcasts (start_time, end_time).
        """
        try:
            # Clear the existing playlist
            self.sp.playlist_replace_items(self.daily_drive_playlist['id'], [])
            
            # Get user's top tracks and artists
            top_tracks = self.sp.current_user_top_tracks(limit=50, time_range='short_term')
            top_artists = self.sp.current_user_top_artists(limit=10, time_range='short_term')
            
            # Train the ML recommender
            self.ml_recommender.train(top_tracks['items'])
            
            # Get recommendations based on top tracks and artists
            seed_tracks = random.sample([track['id'] for track in top_tracks['items']], 2)
            recommendations = self.ml_recommender.get_recommendations(seed_tracks, limit=50)
            
            # Get user's saved podcasts
            saved_shows = self.sp.current_user_saved_shows()
            
            # Calculate the number of tracks and episodes to add
            total_duration = 0
            tracks_to_add = []
            episodes_to_add = []
            
            current_time = datetime.now().time()

            while total_duration < MAX_PLAYLIST_LENGTH:
                if len(recommendations) > 0 and random.random() < music_ratio and self._is_within_time_range(current_time, music_time_range):
                    track_id = recommendations.pop(0)
                    track = self._get_track(track_id)
                    
                    # Check if the track should be excluded
                    if (excluded_artists and any(artist['name'] in excluded_artists for artist in track['artists'])) or \
                    (excluded_genres and any(genre in excluded_genres for genre in track['genres'])) or \
                    (track_id in self.history['tracks']):
                        continue
                    
                    tracks_to_add.append(track_id)
                    total_duration += track['duration_ms']
                    self.history['tracks'].append(track_id)
                elif len(saved_shows['items']) > 0 and self._is_within_time_range(current_time, podcast_time_range):
                    show = random.choice(saved_shows['items'])
                    episodes = self.sp.show_episodes(show['show']['id'])
                    if len(episodes['items']) > 0:
                        episode = episodes['items'][0]
                        if episode['id'] not in self.history['episodes']:
                            episodes_to_add.append(episode['id'])
                            total_duration += episode['duration_ms']
                            self.history['episodes'].append(episode['id'])
            
            # Add tracks and episodes to the playlist
            self.sp.playlist_add_items(self.daily_drive_playlist['id'], tracks_to_add + episodes_to_add)
            
            # Limit history size
            self.history['tracks'] = self.history['tracks'][-1000:]
            self.history['episodes'] = self.history['episodes'][-100:]
            
            # Save updated history
            self._save_history()

            logger.info(f"Daily Drive playlist updated successfully. Added {len(tracks_to_add)} tracks and {len(episodes_to_add)} episodes.")
        except Exception as e:
            logger.error(f"Error updating Daily Drive playlist: {str(e)}")
            raise

    def _is_within_time_range(self, current_time, time_range):
        """Check if the current time is within the specified time range."""
        if not time_range:
            return True
        start_time, end_time = time_range
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:  # Range spans midnight
            return current_time >= start_time or current_time <= end_time

    def _get_track(self, track_id):
        """Get track information with caching."""
        if track_id not in self.cache:
            self.cache[track_id] = self.sp.track(track_id)
        return self.cache[track_id]

    def get_current_playlist(self):
        """
        Get the current Daily Drive playlist.
        
        Returns:
            list: List of track and episode objects in the playlist.
        """
        try:
            return self.sp.playlist_items(self.daily_drive_playlist['id'])
        except Exception as e:
            logger.error(f"Error getting current playlist: {str(e)}")
            raise

    def force_refresh(self):
        """
        Force a refresh of the Daily Drive playlist.
        """
        try:
            self.update_daily_drive()
        except Exception as e:
            logger.error(f"Error forcing playlist refresh: {str(e)}")
            raise

    def get_listening_stats(self):
        """
        Get basic listening statistics.
        
        Returns:
            dict: Dictionary containing listening statistics.
        """
        try:
            top_tracks = self.sp.current_user_top_tracks(limit=10, time_range='short_term')
            top_artists = self.sp.current_user_top_artists(limit=10, time_range='short_term')
            
            return {
                'top_tracks': [{'name': track['name'], 'artist': track['artists'][0]['name']} for track in top_tracks['items']],
                'top_artists': [artist['name'] for artist in top_artists['items']],
                'total_tracks_in_history': len(self.history['tracks']),
                'total_episodes_in_history': len(self.history['episodes'])
            }
        except Exception as e:
            logger.error(f"Error getting listening stats: {str(e)}")
            raise

