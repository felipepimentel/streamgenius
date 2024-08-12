import pytest
from unittest.mock import patch
from src.stream_processor.summarization import summarize

@pytest.fixture
def mock_pipeline():
    with patch('src.stream_processor.summarization.pipeline') as pipeline_mock:
        pipeline_mock.return_value.return_value = [{'summary_text': 'Summarized text'}]
        yield pipeline_mock

def test_summarize(mock_pipeline):
    result = summarize('This is a long text that needs to be summarized.')
    assert result == 'Summarized text'

    mock_pipeline.assert_called_once_with("summarization")
    mock_pipeline.return_value.assert_called_once_with(
        'This is a long text that needs to be summarized.',
        max_length=130,
        min_length=30,
        do_sample=False
    )