import subprocess
import json
from pathlib import Path

def process_spotify(url: str, output_dir: Path):
    """
    Get track information from Spotify and download the audio using spotdl.
    """
    try:
        # Use spotdl to get track info
        result = subprocess.run(["spotdl", "--output", str(output_dir), "--print-errors", "--download-ffmpeg", "--format", "mp3", "--print-json", url], capture_output=True, text=True, check=True)
        track_info = json.loads(result.stdout)

        # Extract relevant information
        info = {
            'name': track_info['name'],
            'artists': [artist['name'] for artist in track_info['artists']],
            'album': track_info['album']['name'],
            'release_date': track_info['album']['release_date'],
            'duration_ms': track_info['duration_ms'],
            'url': url
        }

        # The audio file path
        audio_file = output_dir / f"{track_info['artists'][0]['name']} - {track_info['name']}.mp3"

        return info, audio_file
    except subprocess.CalledProcessError as e:
        print(f"Error processing Spotify URL: {e}")
        print(f"stderr: {e.stderr}")
        raise
    except json.JSONDecodeError:
        print(f"Error decoding JSON from spotdl output")
        print(f"stdout: {result.stdout}")
        raise