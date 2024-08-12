import pytest
from unittest.mock import patch, MagicMock
from src.stream_processor.translation import translate

@pytest.fixture
def mock_marian():
    with patch('src.stream_processor.translation.MarianMTModel.from_pretrained') as model_mock, \
         patch('src.stream_processor.translation.MarianTokenizer.from_pretrained') as tokenizer_mock:
        model_mock.return_value.generate.return_value = [MagicMock()]
        tokenizer_mock.return_value.decode.return_value = 'Texto traduzido'
        yield model_mock, tokenizer_mock

def test_translate(mock_marian):
    result = translate('Test text', 'pt')
    assert result == 'Texto traduzido'

    mock_model, mock_tokenizer = mock_marian
    mock_model.assert_called_once_with('Helsinki-NLP/opus-mt-en-pt')
    mock_tokenizer.assert_called_once_with('Helsinki-NLP/opus-mt-en-pt')