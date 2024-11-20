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
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
CORS(app, resources={r"/*": {"origins": "https://visualify.onrender.com"}})
SPOTIFY_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
REDIRECT_URI = "https://visualifybackend.onrender.com/callback"  # Or your deployed URL
SCOPE = "user-top-read"  # The scope required to access top tracks

@app.route('/login')
def login():
    auth_url = f"{SPOTIFY_AUTHORIZE_URL}?client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}"
    return redirect(auth_url)
# Set up Spotify API credentials

client_credential_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credential_manager)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'json'
def extract_useful_data(json_obj):
    return {
        "timestamp": json_obj.get("ts"),
        "track_name": json_obj.get("master_metadata_track_name"),
        "artist_name": json_obj.get("master_metadata_album_artist_name"),
        "album_name": json_obj.get("master_metadata_album_album_name"),
        "duration_ms": json_obj.get("ms_played"),
        "platform": json_obj.get("platform"),
        "country": json_obj.get("conn_country"),
        "shuffle": json_obj.get("shuffle"),
        "offline": json_obj.get("offline")
    }
spotify_data = {}

@app.route('/analyze')
def analyze():
    access_token = session.get('access_token')
    if not access_token:
        return redirect('/login')

    sp = spotipy.Spotify(auth=access_token)
    top5_tracks = sp.current_user_top_tracks(limit=5)
    top5_artists = sp.current_user_top_artists(limit=5)
    dfTracks = [{
        'name': track['name'],
        'popularity': track['popularity'],
        'artist': track['artists'][0]['name']
    } for track in top5_tracks['items']]

    dfArtists = [{
        'name': artist['name'],
        'popularity': artist['popularity']
    } for artist in top5_artists['items']]

    df_tracks = pd.DataFrame(dfTracks)
    df_artists = pd.DataFrame(dfArtists)

    # Generate plots using Plotly
    track_fig = px.bar(
        df_tracks,
        x='name',
        y='popularity',
        labels={'x': 'Track Name', 'y': 'Popularity'},
        title="Top 5 Tracks by Popularity"
    )

    artist_fig = px.bar(
        df_artists,
        x='name',
        y='popularity',
        labels={'x': 'Artist Name', 'y': 'Popularity'},
        title="Top 5 Artists by Popularity"
    )

    # Convert plots to HTML
    track_html = track_fig.to_html(full_html=False)
    artist_html = artist_fig.to_html(full_html=False)

    # Render an HTML page embedding the plots
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spotify Data Analysis</title>
    </head>
    <body>
        <h1>Spotify Data Analysis</h1>
        <h2>Top 5 Tracks</h2>
        {track_html}

        <h2>Top 5 Artists</h2>
        {artist_html}
    </body>
    </html>
    """
    return render_template_string(html_template)
""" @app.route('/statistics')
def statistics():
    global dfTracks, dfArtists """

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
