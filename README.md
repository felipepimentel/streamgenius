# StreamGenius

StreamGenius is a powerful tool for processing streaming content from YouTube and Spotify. It offers functionalities for transcription, translation, summarization, and content enrichment.

## Features

- Processing of YouTube videos and Spotify tracks
- Audio transcription
- Text translation
- Content summarization
- Text enrichment with synonyms

## Requirements

- Python 3.8+
- Poetry for dependency management

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/streamgenius.git
    cd streamgenius
    ```

2. Install dependencies using Poetry:

    ```bash
    poetry install
    ```

## Usage

1. Activate the Poetry virtual environment:

    ```bash
    poetry shell
    ```

2. Run the main script:

    ```bash
    python src/stream_processor/main.py
    ```

3. When prompted, enter a YouTube or Spotify URL.

4. The script will process the content and return a dictionary with the results of transcription, translation, summarization, and enrichment.

## Project Structure

- `src/stream_processor/`: Contains the main project modules
  - `main.py`: Main entry point
  - `youtube_processor.py`: YouTube video processing
  - `spotify_processor.py`: Spotify track processing
  - `transcription.py`: Audio transcription
  - `translation.py`: Text translation
  - `summarization.py`: Content summarization
  - `enrichment.py`: Text enrichment

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache 2.0 license. See the `LICENSE` file for more details.
