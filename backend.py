from flask import Flask, request, jsonify, redirect, session, render_template, render_template_string
import spotipy
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import os
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from flask_cors import CORS
import json
import requests
import numpy as np
import logging
from spotify_recommender import SpotifyRecommender
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
CORS(app, resources={r"/*": {"origins": "https://visualify.onrender.com"}})
SPOTIFY_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
REDIRECT_URI = "https://visualifybackend.onrender.com/callback"  # Or your deployed URL
SCOPE = "user-top-read user-read-playback-state user-modify-playback-state streaming"

  # The scope required to access top tracks

@app.route('/login')
def login():
    auth_url = f"{SPOTIFY_AUTHORIZE_URL}?client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}"
    return redirect(auth_url)
# Set up Spotify API credentials

client_credential_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credential_manager)

spotify_data = {}

@app.route('/analyze')
def analyze():
    access_token = session.get('access_token')
    if not access_token:
        return redirect('/login')

    sp = spotipy.Spotify(auth=access_token)
    
    # Fetch top tracks and artists
    top5_tracks = sp.current_user_top_tracks(limit=5)
    top5_artists = sp.current_user_top_artists(limit=5)

    #Also get top50 songs and their characteristics to have them as inputs for the cluster model and 
    # for getting the most important characteristics for the listener
    top50_tracks = sp.current_user_top_tracks(limit=50)
    track_ids = [track['id'] for track in top50_tracks['items']]
    audio_features = sp.audio_features(track_ids)
    # Prepare the data
    tracks = [{
        'name': track['name'],
        'artist': track['artists'][0]['name'],
        'album_image': track['album']['images'][0]['url'],
        'id': track['id']  
    } for track in top5_tracks['items']]

    artists = [{
        'name': artist['name'],
        'image': artist['images'][0]['url'] if artist['images'] else None
    } for artist in top5_artists['items']]

    feature_keys = ['danceability', 'energy', 'valence', 'speechiness', 'instrumentalness', 'acousticness']
    average_features = {
        feature: np.mean([track[feature] for track in audio_features if track and track[feature] is not None])
        for feature in feature_keys
    }
    average_features = {k: float(v) for k, v in average_features.items()}

    # Fetch recommended songs (based on the first top track)
    recommendations = []
    if top5_tracks['items']:
        recs = sp.recommendations(seed_tracks=[top5_tracks['items'][0]['id']], limit=3)
        recommendations = [{
            'name': rec['name'],
            'artist': rec['artists'][0]['name'],
            'album_image': rec['album']['images'][0]['url'],
            'id': rec['id']
        } for rec in recs['tracks']]
    #Songs from Spotify 2023 using a ML model
    dataset_path = "spotify-2023.csv"
    recommender = SpotifyRecommender(dataset_path)
    # Get recommendations
    top50_features = [
    {
        "acousticness": feature["acousticness"],
        "danceability": feature["danceability"],
        "energy": feature["energy"],
        "instrumentalness": feature["instrumentalness"],
        "speechiness": feature["speechiness"],
        "valence": feature["valence"]
    }
    for feature in audio_features if feature is not None
]
    recsApp = recommender.get_recommendations(top50_features, n_recommendations=5)
    #Call the API to get the Album picture of the songs
    spotify_data = []
    recs=recsApp[['track_name', 'artist(s)_name']]
    app.logger.info(recs)
    for i in range(0,4):
        query = f"{recs.iloc[i]['track_name']} {recs.iloc[i]['artist(s)_name']}"
        result = sp.search(q=query, type='track', limit=1)
        if result['tracks']['items']:  # Ensure at least one result was found
            track = result['tracks']['items'][0]
            spotify_data.append({
                "name": track['name'],
                "artist": ', '.join(artist['name'] for artist in track['artists']),
                "album_image": track['album']['images'][0]['url'],  # Album cover image
                "id": track['id']  # Spotify track ID
            })
        else:
            spotify_data.append({
                "name": recs['track_name'],
                "artist": recs['artist_name'],
                "album_image": None,  # No album cover if not found
                "id": None  # No track ID if not found
            })




    # Render the template
    return render_template(
        'spotify_unwrapped.html',
        tracks=tracks,
        artists=artists,
        recommendations=recommendations,
        recs=spotify_data,
        average_features=json.dumps(average_features)
    )


@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400
    
    token_url = "https://accounts.spotify.com/api/token"
    try:
        response = requests.post(token_url, data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET
        })

        if response.status_code != 200:
            # Log response content for debugging
            print("Token request failed:", response.content)
            return jsonify({'error': 'Failed to retrieve access token', 'details': response.content}), 500
        
        token_info = response.json()
        access_token = token_info.get("access_token")
        
        if not access_token:
            return jsonify({'error': 'Access token not found in response'}), 500
        
        session['access_token'] = access_token
        return redirect('/analyze')

    except Exception as e:
        print("Error during token exchange:", str(e))
        return jsonify({'error': 'Exception during token exchange', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
