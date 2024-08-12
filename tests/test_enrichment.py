import pytest
from unittest.mock import patch
from src.stream_processor.enrichment import enrich

@pytest.fixture
def mock_nltk():
    with patch('src.stream_processor.enrichment.nltk.word_tokenize') as tokenize_mock, \
         patch('src.stream_processor.enrichment.nltk.pos_tag') as pos_tag_mock, \
         patch('src.stream_processor.enrichment.wordnet.synsets') as synsets_mock:
        tokenize_mock.return_value = ['This', 'is', 'a', 'test']
        pos_tag_mock.return_value = [('This', 'DT'), ('is', 'VBZ'), ('a', 'DT'), ('test', 'NN')]
        synsets_mock.return_value = [MagicMock(lemmas=lambda: [MagicMock(name=lambda: 'exam')])]
        yield

def test_enrich(mock_nltk):
    result = enrich('This is a test')
    assert result == 'This is a test (synonym: exam)'