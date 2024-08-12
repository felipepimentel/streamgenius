import requests
from bs4 import BeautifulSoup
from pathlib import Path

def process_text(url_or_path: str, output_dir: Path):
    """
    Process text content from a URL or local file.
    """
    if url_or_path.startswith(('http://', 'https://')):
        # It's a URL
        response = requests.get(url_or_path)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "Untitled"
        content = ' '.join([p.text for p in soup.find_all('p')])
    else:
        # It's a local file
        file_path = Path(url_or_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {url_or_path}")
        title = file_path.stem
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

    return {
        'title': title,
        'content': content,
        'url': url_or_path
    }