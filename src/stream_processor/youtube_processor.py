import yt_dlp
from pathlib import Path
import time
from openai import OpenAI
import json
from functools import lru_cache
import os
from datetime import datetime
import logging
from typing import Dict, Any
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client (make sure to set your API key in environment variables)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@lru_cache(maxsize=100)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_video_info(url: str) -> Dict[str, Any]:
    """
    Get detailed video information with caching to avoid redundant API calls.
    """
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'force_generic_extractor': True,
        'extract_flat': True,
        'no_warnings': True,
    }
    try:
        async with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'unknown_title'),
                'channel': info.get('uploader', 'unknown_channel'),
                'video_id': info.get('id', 'unknown_id'),
                'description': info.get('description', ''),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'duration': info.get('duration', 0),
                'upload_date': info.get('upload_date', ''),
                'tags': info.get('tags', []),
                'url': url,
            }
    except Exception as e:
        logger.error(f"Error fetching video info: {str(e)}")
        raise

async def process_youtube(url: str, output_dir: Path) -> Dict[str, Any]:
    """
    Download audio from a YouTube video and generate a rich summary.
    """
    audio_file = output_dir / "temp_audio.wav"
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': str(audio_file.with_suffix('')),
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    try:
        async with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await ydl.download([url])
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        raise
    
    video_info = await get_video_info(url)
    summary = await generate_rich_summary(video_info)
    metadata = generate_metadata(video_info)
    
    return {
        'audio_file': audio_file,
        'summary': summary,
        'metadata': metadata
    }

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def generate_rich_summary(video_info: Dict[str, Any]) -> str:
    """
    Generate a rich summary of the video using OpenAI's GPT-4 model.
    """
    prompt = f"""
    Gere um resumo detalhado e envolvente do seguinte vídeo do YouTube em português do Brasil:

    Título: {video_info['title']}
    Canal: {video_info['channel']}
    Descrição: {video_info['description']}
    Visualizações: {video_info['view_count']}
    Likes: {video_info['like_count']}
    Duração: {video_info['duration']} segundos
    Data de upload: {video_info['upload_date']}
    Tags: {', '.join(video_info['tags'])}

    Por favor, inclua os seguintes elementos no formato Markdown:

    1. ## Visão Geral
       - Breve descrição do conteúdo do vídeo (2-3 frases)

    2. ## Pontos-Chave
       - Liste os principais tópicos discutidos (use bullet points)

    3. ## Momentos Notáveis
       - Destaque citações importantes ou momentos marcantes (use blockquotes para citações)

    4. ## Relevância e Importância
       - Explique a importância do vídeo em seu campo ou área de interesse

    5. ## Público-Alvo
       - Descreva quem se beneficiaria mais ao assistir este vídeo e por quê

    6. ## Controvérsias ou Debates (se aplicável)
       - Mencione quaisquer pontos de discussão ou debates relacionados ao tema

    7. ## Tópicos Relacionados
       - Sugira outros vídeos ou temas que os espectadores possam achar interessantes

    Faça o resumo envolvente, informativo e com cerca de 400-500 palavras. Use formatação Markdown para melhorar a legibilidade.
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em criar resumos detalhados e envolventes de vídeos do YouTube em português do Brasil."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            n=1,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise

def generate_metadata(video_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate metadata for the processed video.
    """
    return {
        "video_url": video_info['url'],
        "video_title": video_info['title'],
        "channel_name": video_info['channel'],
        "video_upload_date": video_info['upload_date'],
        "video_duration": video_info['duration'],
        "view_count": video_info['view_count'],
        "like_count": video_info['like_count'],
        "processing_date": datetime.now().isoformat(),
        "tags": video_info['tags'],
    }

# Example usage
if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    output_dir = Path("./output")
    audio_file, summary, metadata = asyncio.run(process_youtube(url, output_dir))
    print(f"Audio file saved as: {audio_file}")
    print("\nVideo Summary:")
    print(summary)
    print("\nMetadata:")
    print(json.dumps(metadata, indent=2))