import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import json

class SpotifyRecommender:
    def __init__(self, dataset):
        """
        Initialize the recommender system with the Spotify 2023 dataset
        """
        # Load the spotify 2023 dataset
        if isinstance(dataset, str):
            self.df = pd.read_csv(dataset)
        else:
            self.df = dataset
            
        # Define features and their mapping from Spotify API to our dataset
        self.feature_mapping = {
            'danceability': 'danceability_%',
            'energy': 'energy_%',
            'valence': 'valence_%',
            'speechiness': 'speechiness_%',
            'instrumentalness': 'instrumentalness_%',
            'acousticness': 'acousticness_%'
        }
        
        self.features = list(self.feature_mapping.values())
        
        # Clean and prepare the data
        self.prepare_data()
        
    def prepare_data(self):
        """
        Prepare the data by scaling features and handling any missing values
        """
        # Convert features to numeric, replacing any non-numeric values with NaN
        for feature in self.features:
            self.df[feature] = pd.to_numeric(self.df[feature], errors='coerce')
            
        # Fill any missing values with the median
        for feature in self.features:
            self.df[feature].fillna(self.df[feature].median(), inplace=True)
        
        # Scale the features
        self.scaler = StandardScaler()
        self.features_scaled = self.scaler.fit_transform(self.df[self.features])
        
    def process_spotify_api_features(self, spotify_features_list):
        """
        Convert Spotify API features to the format matching our dataset
        """
        processed_features = []
        
        for track in spotify_features_list:
            # Convert to dict if it's a string
            if isinstance(track, str):
                track = json.loads(track)
                
            # Convert features to percentages to match our dataset
            processed_track = {}
            for api_feature, our_feature in self.feature_mapping.items():
                processed_track[our_feature] = track[api_feature] * 100
                
            processed_features.append(processed_track)
            
        return pd.DataFrame(processed_features)
    
    def get_recommendations_from_spotify_features(self, spotify_features_list, n_recommendations=10):
        """
        Get recommendations based on Spotify API audio features
        
        Parameters:
        spotify_features_list: List of dictionaries containing Spotify API audio features
        n_recommendations: Number of recommendations to return
        """
        # Process the Spotify API features
        user_features_df = self.process_spotify_api_features(spotify_features_list)
        
        # Scale the user features using the same scaler
        user_features_scaled = self.scaler.transform(user_features_df[self.features])
        
        # Calculate mean feature vector of user's songs
        user_profile = np.mean(user_features_scaled, axis=0).reshape(1, -1)
        
        # Calculate cosine similarity between user profile and all songs
        similarities = cosine_similarity(user_profile, self.features_scaled)
        
        # Get indices of most similar songs
        similar_indices = similarities.argsort()[0][::-1][:n_recommendations]
        
        # Create recommendations DataFrame
        recommendations = self.df.iloc[similar_indices].copy()
        recommendations['similarity_score'] = similarities[0][similar_indices]
        
        # Select relevant columns for display
        display_columns = ['track_name', 'artist(s)_name', 'similarity_score'] + self.features
        
        return recommendations[display_columns].sort_values('similarity_score', ascending=False)