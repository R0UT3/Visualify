
from flask import Flask, request, jsonify, redirect, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
from flask_cors import CORS
import json
import requests
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')





app = Flask(__name__)
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
@app.route('/analyze')
def analyze():
    access_token = session.get('access_token')
    if not access_token:
        return redirect('/login')

    sp = spotipy.Spotify(auth=access_token)
    user_tracks = sp.current_user_top_tracks(limit=50)
    track_names = [track['name'] for track in user_tracks['items']]
    return jsonify(track_names)

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
    
@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = "https://accounts.spotify.com/api/token"
    response = requests.post(token_url, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    })

    token_info = response.json()
    access_token = token_info.get("access_token")
    session['access_token'] = access_token
    return redirect('/analyze')

if __name__ == '__main__':
    app.run(debug=True)
