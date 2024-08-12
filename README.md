# StreamGenius 🎵🎥

StreamGenius is a powerful Python tool for processing streaming content from YouTube and Spotify. It offers advanced functionalities for audio transcription, text translation, content summarization, and text enrichment.

## 🌟 Features

- 🎥 Process YouTube videos
- 🎵 Handle Spotify tracks and podcasts
- 🎙️ Accurate audio transcription using Whisper AI
- 🌐 Text translation to multiple languages
- 📝 Intelligent content summarization
- 🔤 Text enrichment with synonyms
- 📊 Metadata extraction and processing

## 🛠️ Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/streamgenius.git
   cd streamgenius
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Set up environment variables:
   Create a `.env` file in the project root and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   ```

## 🚀 Usage

1. Activate the Poetry virtual environment:
   ```
   poetry shell
   ```

2. Run the main script with a YouTube or Spotify URL:
   ```
   python -m src.stream_processor.main <URL> [--output OUTPUT_DIR] [--model MODEL_SIZE]
   ```

   Options:
   - `<URL>`: The YouTube video or Spotify track URL (required)
   - `--output OUTPUT_DIR`: Specify the output directory for results (optional)
   - `--model MODEL_SIZE`: Choose the Whisper model size: tiny, base, small, medium, or large (default: tiny)

3. The script will process the content and save the results in the specified output directory or the default `streamgenius_output` folder in your home directory.

## 📁 Project Structure

- `src/stream_processor/`: Contains the main project modules
  - `main.py`: Main entry point
  - `youtube_processor.py`: YouTube video processing
  - `spotify_processor.py`: Spotify track processing
  - `transcription.py`: Audio transcription
  - `translation.py`: Text translation
  - `summarization.py`: Content summarization
  - `enrichment.py`: Text enrichment
- `tests/`: Contains unit tests for the project

## 🧪 Running Tests

To run the unit tests, use the following command:
```
pytest
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) for audio transcription
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube video downloading
- [spotdl](https://github.com/spotDL/spotify-downloader) for Spotify track downloading
- [Transformers](https://github.com/huggingface/transformers) for NLP tasks