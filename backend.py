from flask import Flask, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import json
load_dotenv()

app = Flask(__name__)

# Set up Spotify API credentials

client_credential_manager = SpotifyClientCredentials(client_id="SPOTIFY_CLIENT_ID", client_secret="SPOTIFY_CLIENT_SECRET")
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
@app.route('/analyze', methods=['POST'])
def analyze():
    print("HELOO")
    data = request.json
    username = data.get('username')
    if username:
        # Handle the case where the user inputs their Spotify username
        try:
            user_tracks = sp.current_user_top_tracks(limit=50)
            # Extract track names and other data
            track_names = [track['name'] for track in user_tracks['items']]

            # You will need to process the track names through the Spotify API for danceability, etc.

            # Placeholder for model results (replace with actual model calls)
            model_results = {"message": "Model predictions would go here."}
            return jsonify({'tracks': track_names, 'model_results': model_results})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

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
    
    
@app.route('/callback', methods=['POST'])
def callback():
    data = request.json
    auth_code = data.get('code')

    if not auth_code:
        return jsonify({'success': False, 'error': 'No authorization code provided'})

    try:
        # Exchange the authorization code for an access token
        token_info = sp.get_access_token(auth_code)

        # Save token info in session (or handle it securely)
        #session['token_info'] = token_info

        return jsonify({'success': True})  # Let the frontend know everything is good
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500 """


if __name__ == '__main__':
    app.run(debug=True)
