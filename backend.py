
from flask import Flask, request, jsonify, redirect, session
import spotipy
from dash import Dash, html, dcc
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import os
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
    track_names = [track['name'] for track in top5_tracks['items']]
    spotify_data['top_tracks'] = [{
            'name': track['name'],
            'popularity': track['popularity'],
            'artist': track['artists'][0]['name']
        } for track in top5_tracks['items']]

    spotify_data['top_artists'] = [{
            'name': artist['name'],
            'popularity': artist['popularity']
        } for artist in top5_artists['items']]
    return redirect('/dash')

"""     # Case 2: User uploads a JSON file
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']

    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        filename = file.filename
        file_data = file.read().decode('utf-8')

        try:
            json_data = json.loads(file_data)

            # If it's a list of JSON objects (like streaming history):
            if isinstance(json_data, list):
                extracted_data_list = [extract_useful_data(item) for item in json_data]
            else:
                # Handle the case where it's a single JSON object
                extracted_data_list = [extract_useful_data(json_data)]

            return jsonify(extracted_data_list)

        except json.JSONDecodeError:
            return "Invalid JSON file", 400

    return "Invalid file format", 400
    # Fetch Spotify data for this user
    """
dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')

# Layout for Dash
dash_app.layout = html.Div([
    html.H1("Spotify Data Visualization"),
    
    html.H2("Top 5 Tracks"),
    dcc.Graph(id='top-tracks-graph'),

    html.H2("Top 5 Artists"),
    dcc.Graph(id='top-artists-graph'),

    html.H2("Recommended Songs Based on Top Tracks"),
    dcc.Graph(id='recommended-tracks-graph')
])  
# Callbacks to update graphs
@dash_app.callback(
    [dcc.Output('top-tracks-graph', 'figure'),
     dcc.Output('top-artists-graph', 'figure'),
     dcc.Output('recommended-tracks-graph', 'figure')],
    []
)
def update_graphs():
    top_tracks = spotify_data.get('top_tracks', [])
    top_artists = spotify_data.get('top_artists', [])

    # Top Tracks Graph
    top_tracks_fig = px.bar(
        x=[track['name'] for track in top_tracks],
        y=[track['popularity'] for track in top_tracks],
        labels={'x': 'Track', 'y': 'Popularity'},
        title="Top 5 Tracks by Popularity"
    )

    # Top Artists Graph
    top_artists_fig = px.bar(
        x=[artist['name'] for artist in top_artists],
        y=[artist['popularity'] for artist in top_artists],
        labels={'x': 'Artist', 'y': 'Popularity'},
        title="Top 5 Artists by Popularity"
    )

    # Placeholder for recommended songs (similar songs to top tracks)
    recommended_fig = px.bar(
        x=["Song A", "Song B", "Song C", "Song D", "Song E"],  # Placeholder names
        y=[80, 75, 85, 78, 82],  # Placeholder scores
        labels={'x': 'Recommended Song', 'y': 'Similarity Score'},
        title="Recommended Songs Based on Top Tracks"
    )

    return top_tracks_fig, top_artists_fig, recommended_fig 
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
