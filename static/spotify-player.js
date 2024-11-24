let player = null;
let deviceId = null;
let currentlyPlaying = null;

window.onSpotifyWebPlaybackSDKReady = () => {
    const token = document.querySelector('body').dataset.accessToken;

    player = new Spotify.Player({
        name: 'Visualify Web Player',
        getOAuthToken: (cb) => {
            cb(token);
        },
    });

    // Error handling
    player.addListener('initialization_error', ({ message }) => {
        console.error('Failed to initialize', message);
    });
    player.addListener('authentication_error', ({ message }) => {
        console.error('Failed to authenticate', message);
    });
    player.addListener('account_error', ({ message }) => {
        console.error('Failed to validate Spotify account', message);
    });
    player.addListener('playback_error', ({ message }) => {
        console.error('Failed to perform playback', message);
    });

    // Playback status updates
    player.addListener('player_state_changed', (state) => {
        if (state) {
            updatePlaybackState(state);
        }
    });

    // Ready
    player.addListener('ready', ({ device_id }) => {
        console.log('Ready with Device ID', device_id);
        deviceId = device_id;
    });

    // Connect to the player
    player.connect();
};

// Handle clicks on tracks
function initializeTrackClickHandlers() {
    document.querySelectorAll('.item').forEach((item) => {
        item.addEventListener('click', async () => {
            if (!player || !deviceId) {
                console.error('Player not ready');
                return;
            }

            const trackId = item.dataset.trackId;

            if (currentlyPlaying === trackId) {
                // Pause the currently playing track
                await fetch(
                    `https://api.spotify.com/v1/me/player/pause?device_id=${deviceId}`,
                    {
                        method: 'PUT',
                        headers: {
                            Authorization: `Bearer ${document
                                .querySelector('body')
                                .dataset.accessToken}`,
                        },
                    }
                );
                item.classList.remove('playing');
                currentlyPlaying = null;
            } else {
                // Play the clicked track
                await fetch(
                    `https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`,
                    {
                        method: 'PUT',
                        headers: {
                            Authorization: `Bearer ${document
                                .querySelector('body')
                                .dataset.accessToken}`,
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            uris: [`spotify:track:${trackId}`],
                        }),
                    }
                );

                // Update UI
                document.querySelectorAll('.item').forEach((el) => {
                    el.classList.remove('playing');
                });
                item.classList.add('playing');
                currentlyPlaying = trackId;
            }
        });
    });
}

function updatePlaybackState(state) {
    const isPlaying = !state.paused;
    const currentTrackId = state.track_window.current_track.id;

    document.querySelectorAll('.item').forEach((item) => {
        if (item.dataset.trackId === currentTrackId && isPlaying) {
            item.classList.add('playing');
        } else {
            item.classList.remove('playing');
        }
    });
}

// Initialize click handlers
document.addEventListener('DOMContentLoaded', () => {
    initializeTrackClickHandlers();
});
