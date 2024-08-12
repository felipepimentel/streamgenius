import os
import subprocess
import torch
import whisper
from pathlib import Path
from deep_translator import GoogleTranslator
from langdetect import detect
from transformers import pipeline
import argparse
import warnings
import json
from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
from stream_processor.youtube_processor import get_video_info, process_youtube
from stream_processor.spotify_processor import process_spotify
from stream_processor.text_processor import process_text
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time

# Suppress Numba deprecation warnings
warnings.filterwarnings("ignore", category=NumbaDeprecationWarning)
warnings.filterwarnings("ignore", category=NumbaPendingDeprecationWarning)

# Suppress the FutureWarning specific to clean_up_tokenization_spaces
warnings.filterwarnings("ignore", category=FutureWarning, message=".*clean_up_tokenization_spaces.*")

# Initialize Spotify client
client_credentials_manager = SpotifyClientCredentials(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def create_output_directory():
    output_dir = Path.home() / "streamgenius_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def split_audio(audio_file, chunk_duration=30):
    """Split audio file into chunks."""
    from pydub import AudioSegment
    audio = AudioSegment.from_wav(audio_file)
    chunks = []
    for i in range(0, len(audio), chunk_duration * 1000):
        chunks.append(audio[i:i + chunk_duration * 1000])
    return chunks

def transcribe_audio(audio_file: Path, model_size="tiny"):
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    
    # Load the model with FP32 precision
    model = whisper.load_model(model_size, device="cpu", in_memory=True)
    
    # Transcribe with FP32 precision
    result = model.transcribe(str(audio_file), fp16=False)
    
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    return result["text"]

def translate_text(text, target_lang='pt'):
    detected_lang = detect(text)
    translator = GoogleTranslator(source=detected_lang, target=target_lang)
    
    # Split text into smaller parts if it's too long
    max_length = 4999
    parts = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    
    translated_text = ""
    for part in parts:
        translated_text += translator.translate(part) + " "
    
    return translated_text.strip()

def summarize_text(text, max_length=150, max_input_length=1024):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # Split the text into smaller chunks
    chunks = [text[i:i+max_input_length] for i in range(0, len(text), max_input_length)]
    
    summaries = []
    for chunk in chunks:
        # Adjust max_length based on input length
        chunk_length = len(chunk.split())  # Count words instead of characters
        
        # Set max_length to be about half the input length, but not less than 30 or more than 150
        adjusted_max_length = max(30, min(chunk_length // 2, 150))
        
        # Ensure max_length is always less than input length
        if adjusted_max_length >= chunk_length:
            adjusted_max_length = max(30, chunk_length - 1)
        
        summary = summarizer(chunk, max_length=adjusted_max_length, min_length=30, do_sample=False, clean_up_tokenization_spaces=True)
        summaries.append(summary[0]['summary_text'])
    
    # Combine the summaries
    final_summary = " ".join(summaries)
    
    # If the combined summary is still too long, summarize it again
    if len(final_summary.split()) > max_length:
        final_summary = summarize_text(final_summary, max_length, max_input_length)
    
    return final_summary

def generate_spotify_summary(spotify_info):
    if spotify_info['type'] == 'track':
        prompt = f"""
        Gere um resumo detalhado e envolvente da seguinte faixa do Spotify em português do Brasil:

        Nome: {spotify_info['name']}
        Artista(s): {', '.join(spotify_info['artists'])}
        Álbum: {spotify_info['album']}
        Data de lançamento: {spotify_info['release_date']}
        Duração: {spotify_info['duration_ms'] // 1000} segundos

        Por favor, inclua os seguintes elementos no formato Markdown:

        1. ## Visão Geral
           - Breve descrição do conteúdo da faixa (2-3 frases)

        2. ## Destaques
           - Liste os principais aspectos ou características notáveis

        3. ## Contexto e Importância
           - Explique a relevância desta faixa no contexto da carreira do artista ou do gênero musical

        4. ## Público-Alvo
           - Descreva quem provavelmente mais apreciaria esta música e por quê

        5. ## Recomendações Relacionadas
           - Sugira outras faixas, álbuns ou artistas que os ouvintes possam gostar

        Faça o resumo envolvente, informativo e com cerca de 300-400 palavras. Use formatação Markdown para melhorar a legibilidade.
        """
    else:  # episode
        prompt = f"""
        Gere um resumo detalhado e envolvente do seguinte episódio de podcast do Spotify em português do Brasil:

        Nome do episódio: {spotify_info['name']}
        Podcast: {spotify_info['show']}
        Data de lançamento: {spotify_info['release_date']}
        Duração: {spotify_info['duration_ms'] // 1000} segundos

        Descrição do episódio:
        {spotify_info['description']}

        Por favor, inclua os seguintes elementos no formato Markdown:

        1. ## Visão Geral
           - Breve descrição do conteúdo do episódio (2-3 frases)

        2. ## Principais Tópicos
           - Liste os principais tópicos ou temas discutidos no episódio

        3. ## Relevância e Contexto
           - Explique a importância deste episódio no contexto do podcast ou do tema geral

        4. ## Público-Alvo
           - Descreva quem provavelmente mais se interessaria por este episódio e por quê

        5. ## Episódios Relacionados
           - Sugira outros episódios deste ou de outros podcasts que os ouvintes possam gostar

        Faça o resumo envolvente, informativo e com cerca de 300-400 palavras. Use formatação Markdown para melhorar a legibilidade.
        """

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em criar resumos detalhados e envolventes de conteúdo do Spotify em português do Brasil."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                n=1,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Tentativa {attempt + 1} de chamada à API OpenAI falhou: {str(e)}")
            time.sleep(5)
    raise Exception("Falha ao gerar o resumo após 3 tentativas")

def process_spotify(url: str, output_dir: Path):
    """
    Get track or episode information from Spotify.
    """
    try:
        # Extract Spotify ID from URL
        if 'track' in url:
            spotify_id = url.split('track/')[1].split('?')[0]
            track = sp.track(spotify_id)
            info = {
                'type': 'track',
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'album': track['album']['name'],
                'release_date': track['album']['release_date'],
                'duration_ms': track['duration_ms'],
                'url': url
            }
            # Attempt to download using spotdl
            try:
                result = subprocess.run(
                    ["spotdl", "--output", str(output_dir), "--print-errors", "--format", "mp3", url],
                    capture_output=True, text=True, check=True, input='n\n', encoding='utf-8'
                )
                file_name = f"{info['artists'][0]} - {info['name']}.mp3"
                audio_file = output_dir / file_name
            except subprocess.CalledProcessError:
                print("Warning: Unable to download audio. Proceeding with metadata only.")
                audio_file = None
        elif 'episode' in url:
            spotify_id = url.split('episode/')[1].split('?')[0]
            episode = sp.episode(spotify_id)
            info = {
                'type': 'episode',
                'name': episode['name'],
                'show': episode['show']['name'],
                'release_date': episode['release_date'],
                'duration_ms': episode['duration_ms'],
                'description': episode['description'],
                'url': url
            }
            print("Note: Spotify podcast episodes cannot be downloaded directly. Only metadata is available.")
            audio_file = None
        else:
            raise ValueError("Unsupported Spotify content type")

        return info, audio_file

    except Exception as e:
        print(f"Error processing Spotify content: {str(e)}")
        raise

def main(url, output_dir=None, model_size="tiny"):
    # Use the provided output directory or create a default one
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = create_output_directory()

    youtube_data = None  # Initialize youtube_data to None

    if "youtube.com" in url or "youtu.be" in url:
        # Process YouTube video
        video_info = get_video_info(url)
        title = video_info['title']
        channel = video_info['channel']
        video_id = video_info['video_id']
        print(f"Title: {title}")
        print(f"Channel: {channel}")

        try:
            youtube_data = process_youtube(url, output_dir)
            print(f"Audio file saved as: {youtube_data['audio_file']}")
        except Exception as e:
            print(f"Warning: Error during YouTube processing - {str(e)}")
            print("Continuing with available data...")
    elif "spotify.com" in url:
        # Process Spotify track or episode
        try:
            spotify_info, audio_file = process_spotify(url, output_dir)
            title = spotify_info['name']
            content_type = spotify_info['type']
            
            if content_type == 'track':
                artists = ", ".join(spotify_info['artists'])
                print(f"Track: {title}")
                print(f"Artist(s): {artists}")
            else:
                show = spotify_info['show']
                print(f"Episode: {title}")
                print(f"Podcast: {show}")
            
            # Generate a summary for Spotify content
            spotify_summary = generate_spotify_summary(spotify_info)
            
            # If audio file is available, transcribe and process it
            if audio_file and audio_file.exists():
                print("Transcribing audio...")
                transcript = transcribe_audio(audio_file, model_size)
                print("Translating transcript...")
                translated_transcript = translate_text(transcript)
                print("Generating summary...")
                summary = summarize_text(translated_transcript, max_length=200, max_input_length=1024)
            else:
                transcript = "Audio não disponível para transcrição."
                translated_transcript = "Audio não disponível para tradução."
                summary = "Resumo no disponível devido à falta de áudio."
            
            # Save results
            output_file = output_dir / f"{title}.md".replace(" ", "_")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                if content_type == 'track':
                    f.write(f"**Artista(s):** {artists}\n\n")
                else:
                    f.write(f"**Podcast:** {show}\n\n")
                f.write("## Informações do Spotify\n\n")
                f.write("```json\n")
                f.write(json.dumps(spotify_info, indent=2, ensure_ascii=False))
                f.write("\n```\n\n")
                f.write("## Resumo do Conteúdo\n\n")
                f.write(spotify_summary)
                f.write("\n\n## Transcrição Original\n\n")
                f.write("```\n")
                f.write(transcript)
                f.write("\n```\n\n")
                f.write("## Transcrição em Português\n\n")
                f.write("```\n")
                f.write(translated_transcript)
                f.write("\n```\n\n")
                f.write("## Resumo da Transcrição\n\n")
                f.write(summary)
            
            print(f"Resultados salvos em {output_file}")

            # Clean up
            if audio_file and audio_file.exists():
                audio_file.unlink()

        except Exception as e:
            print(f"Erro ao processar conteúdo do Spotify: {str(e)}")
        return
    else:
        # Process text content (blog or local file)
        try:
            text_info = process_text(url, output_dir)
            title = text_info['title']
            content = text_info['content']
            print(f"Title: {title}")
            
            # Translate content
            print("Translating content...")
            translated_content = translate_text(content)

            # Summarize content
            print("Generating summary...")
            summary = summarize_text(translated_content, max_length=200, max_input_length=1024)
            
            # Save results
            output_file = output_dir / f"{title}.md".replace(" ", "_")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(f"**Source:** {text_info['url']}\n\n")
                f.write("## Original Content\n\n")
                f.write("```\n")
                f.write(content[:1000] + "..." if len(content) > 1000 else content)
                f.write("\n```\n\n")
                f.write("## Translated Content\n\n")
                f.write("```\n")
                f.write(translated_content[:1000] + "..." if len(translated_content) > 1000 else translated_content)
                f.write("\n```\n\n")
                f.write("## Summary\n\n")
                f.write(summary)

            print(f"Results saved in {output_file}")

        except Exception as e:
            print(f"Error processing text content: {str(e)}")
        return

    if youtube_data is None or not youtube_data['audio_file'].exists():
        print("Error: Audio file not found or not downloaded.")
        return

    # Transcribe audio
    print("Transcribing audio...")
    transcript = transcribe_audio(youtube_data['audio_file'], model_size)

    # Translate transcript
    print("Translating transcript...")
    translated_transcript = translate_text(transcript)

    # Summarize transcript
    print("Generating summary...")
    summary = summarize_text(translated_transcript, max_length=200, max_input_length=1024)

    # Save results
    output_file = output_dir / f"{youtube_data['channel']}_{youtube_data['title']}.md".replace(" ", "_")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# {youtube_data['title']}\n\n")
        f.write(f"**Canal/Artista:** {youtube_data['channel']}\n\n")
        
        f.write("## Transcrição Original\n\n")
        f.write("```\n")
        f.write(transcript)
        f.write("\n```\n\n")
        
        f.write("## Transcrição em Português\n\n")
        f.write("```\n")
        f.write(translated_transcript)
        f.write("\n```\n\n")
        
        f.write("## Resumo Detalhado\n\n")
        f.write(youtube_data['summary'])
        
        f.write("\n\n## Metadados\n\n")
        f.write("```json\n")
        f.write(json.dumps(youtube_data['metadata'], indent=2, ensure_ascii=False))
        f.write("\n```\n")

    print(f"Resultados salvos em {output_file}")

    # Clean up
    if youtube_data['audio_file'].exists():
        youtube_data['audio_file'].unlink()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process streaming content from YouTube, Spotify, or text sources.")
    parser.add_argument("url", help="URL of the YouTube video, Spotify track, blog post, or path to a local file")
    parser.add_argument("--output", help="Output directory for results (optional)")
    parser.add_argument("--model", choices=["tiny", "base", "small", "medium", "large"], default="tiny", help="Whisper model size (default: tiny)")
    args = parser.parse_args()
    
    # Try to update yt-dlp, but don't stop execution if it fails
    try:
        subprocess.run(["pip", "install", "--upgrade", "yt-dlp"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Warning: Failed to update yt-dlp. Continuing with the installed version.")
    
    main(args.url, args.output, args.model)