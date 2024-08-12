import pytest
from unittest.mock import patch, MagicMock
import torch
from src.stream_processor.transcription import transcribe

@pytest.fixture
def mock_wav2vec2():
    with patch('src.stream_processor.transcription.Wav2Vec2Tokenizer.from_pretrained') as tokenizer_mock, \
         patch('src.stream_processor.transcription.Wav2Vec2ForCTC.from_pretrained') as model_mock, \
         patch('src.stream_processor.transcription.sf.read') as sf_mock:
        tokenizer_mock.return_value.batch_decode.return_value = ['Transcribed text']
        model_mock.return_value.return_value.logits = torch.rand(1, 10, 32)
        sf_mock.return_value = (MagicMock(), MagicMock())
        yield tokenizer_mock, model_mock

def test_transcribe(mock_wav2vec2):
    result = transcribe('test_audio.wav')
    assert result == 'Transcribed text'

    tokenizer_mock, model_mock = mock_wav2vec2
    tokenizer_mock.assert_called_once_with("facebook/wav2vec2-base-960h")
    model_mock.assert_called_once_with("facebook/wav2vec2-base-960h")