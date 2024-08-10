# StreamGenius

StreamGenius é uma ferramenta poderosa para processar conteúdo de streaming do YouTube e Spotify. Ela oferece funcionalidades de transcrição, tradução, resumo e enriquecimento de conteúdo.

## Funcionalidades

- Processamento de vídeos do YouTube e faixas do Spotify
- Transcrição de áudio
- Tradução de texto
- Resumo de conteúdo
- Enriquecimento de texto com sinônimos

## Requisitos

- Python 3.8+
- Poetry para gerenciamento de dependências

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/streamgenius.git
   cd streamgenius
   ```

2. Instale as dependências usando Poetry:
   ```
   poetry install
   ```

## Uso

1. Ative o ambiente virtual do Poetry:
   ```
   poetry shell
   ```

2. Execute o script principal:
   ```
   python src/stream_processor/main.py
   ```

3. Quando solicitado, insira uma URL do YouTube ou Spotify.

4. O script processará o conteúdo e retornará um dicionário com os resultados de transcrição, tradução, resumo e enriquecimento.

## Estrutura do Projeto

- `src/stream_processor/`: Contém os módulos principais do projeto
  - `main.py`: Ponto de entrada principal
  - `youtube_processor.py`: Processamento de vídeos do YouTube
  - `spotify_processor.py`: Processamento de faixas do Spotify
  - `transcription.py`: Transcrição de áudio
  - `translation.py`: Tradução de texto
  - `summarization.py`: Resumo de conteúdo
  - `enrichment.py`: Enriquecimento de texto

## Contribuindo

Contribuições são bem-vindas! Por favor, sinta-se à vontade para submeter um Pull Request.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
