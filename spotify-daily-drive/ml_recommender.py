import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict

class MLRecommender:
    def __init__(self, sp):
        """
        Initialize the MLRecommender.
        
        Args:
            sp (spotipy.Spotify): Authenticated Spotify client.
        """
        self.sp = sp
        self.model = KMeans(n_clusters=5)
        self.user_vector = None
        self.track_features = defaultdict(dict)

    def _get_audio_features(self, track_ids):
        """
        Get audio features for a list of track IDs.
        
        Args:
            track_ids (list): List of Spotify track IDs.
        
        Returns:
            list: List of audio feature dictionaries.
        """
        features = self.sp.audio_features(track_ids)
        return [f for f in features if f is not None]

    def train(self, top_tracks):
        """
        Train the model on the user's top tracks.
        
        Args:
            top_tracks (list): List of the user's top track objects.
        """
        track_ids = [track['id'] for track in top_tracks]
        audio_features = self._get_audio_features(track_ids)
        
        X = np.array([[f['danceability'], f['energy'], f['valence']] for f in audio_features])
        self.model.fit(X)
        
        self.user_vector = np.mean(X, axis=0)
        
        for track, features in zip(top_tracks, audio_features):
            self.track_features[track['id']] = {
                'danceability': features['danceability'],
                'energy': features['energy'],
                'valence': features['valence']
            }

    def get_recommendations(self, seed_tracks, limit=50):
        """
        Get recommendations based on seed tracks and user preferences.
        
        Args:
            seed_tracks (list): List of seed track IDs.
            limit (int): Number of recommendations to return.
        
        Returns:
            list: List of recommended track IDs.
        """
        recommendations = self.sp.recommendations(seed_tracks=seed_tracks, limit=limit)
        rec_tracks = recommendations['tracks']
        rec_ids = [track['id'] for track in rec_tracks]
        rec_features = self._get_audio_features(rec_ids)
        
        scores = []
        for track, features in zip(rec_tracks, rec_features):
            if features is None:
                continue
            track_vector = np.array([features['danceability'], features['energy'], features['valence']])
            distance = np.linalg.norm(self.user_vector - track_vector)
            scores.append((track['id'], distance))
        
        scores.sort(key=lambda x: x[1])
        return [track_id for track_id, _ in scores[:limit]]

