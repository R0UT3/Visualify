from flask import Flask, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

# Set up Spotify API credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="your_client_id",
                                               client_secret="your_client_secret",
                                               redirect_uri="http://localhost:5000/callback",
                                               scope="user-top-read"))

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({'error': 'Username required'}), 400

    # Fetch Spotify data for this user
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

if __name__ == '__main__':
    app.run(debug=True)
