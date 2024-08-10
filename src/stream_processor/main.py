from stream_processor.youtube_processor import process_youtube
import yt_dlp as youtube_dl
from stream_processor.spotify_processor import process_spotify
from stream_processor.transcription import transcribe
from stream_processor.translation import translate
from stream_processor.summarization import summarize
from stream_processor.enrichment import enrich

def process_stream(url: str):
    """
    Main function to process a stream from YouTube or Spotify.
    """
    if "youtube.com" in url or "youtu.be" in url:
        audio = process_youtube(url)
    elif "spotify.com" in url:
        audio = process_spotify(url)
    else:
        raise ValueError("Unsupported URL. Please provide a YouTube or Spotify URL.")

    transcript = transcribe(audio)
    translation = translate(transcript)
    summary = summarize(translation)
    enriched = enrich(summary)

    return {
        "transcript": transcript,
        "translation": translation,
        "summary": summary,
        "enriched": enriched
    }

if __name__ == "__main__":
    url = input("Enter a YouTube or Spotify URL: ")
    result = process_stream(url)
    print(result)
