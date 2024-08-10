import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def process_spotify(url: str):
    """
    Get track information from Spotify.
    Note: This function doesn't actually download the audio due to legal restrictions.
    It only retrieves track information.
    """
    # Initialize Spotify client
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Get track ID from URL
    track_id = url.split('/')[-1].split('?')[0]

    # Get track information
    track_info = sp.track(track_id)

    return track_info
