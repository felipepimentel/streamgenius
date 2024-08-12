import pytest
from unittest.mock import patch, MagicMock
from src.stream_processor.youtube_processor import get_video_info, process_youtube, generate_rich_summary, generate_metadata

@pytest.fixture
def mock_yt_dlp():
    with patch('src.stream_processor.youtube_processor.yt_dlp.YoutubeDL') as mock:
        yield mock

@pytest.fixture
def mock_openai():
    with patch('src.stream_processor.youtube_processor.client.chat.completions.create') as mock:
        yield mock

def test_get_video_info(mock_yt_dlp):
    mock_yt_dlp.return_value.extract_info.return_value = {
        'title': 'Test Video',
        'uploader': 'Test Channel',
        'id': 'test_id',
        'description': 'Test description',
        'view_count': 1000,
        'like_count': 100,
        'duration': 300,
        'upload_date': '20230101',
        'tags': ['tag1', 'tag2'],
    }

    url = 'https://www.youtube.com/watch?v=test_id'
    result = get_video_info(url)

    assert result['title'] == 'Test Video'
    assert result['channel'] == 'Test Channel'
    assert result['video_id'] == 'test_id'
    assert result['view_count'] == 1000
    assert result['like_count'] == 100
    assert result['duration'] == 300
    assert result['upload_date'] == '20230101'
    assert result['tags'] == ['tag1', 'tag2']
    assert result['url'] == url

def test_generate_rich_summary(mock_openai):
    mock_openai.return_value.choices[0].message.content = 'Test summary'
    video_info = {
        'title': 'Test Video',
        'channel': 'Test Channel',
        'description': 'Test description',
        'view_count': 1000,
        'like_count': 100,
        'duration': 300,
        'upload_date': '20230101',
        'tags': ['tag1', 'tag2'],
    }

    result = generate_rich_summary(video_info)

    assert result == 'Test summary'

def test_generate_metadata():
    video_info = {
        'url': 'https://www.youtube.com/watch?v=test_id',
        'title': 'Test Video',
        'channel': 'Test Channel',
        'upload_date': '20230101',
        'duration': 300,
        'view_count': 1000,
        'like_count': 100,
        'tags': ['tag1', 'tag2'],
    }

    result = generate_metadata(video_info)

    assert result['video_url'] == 'https://www.youtube.com/watch?v=test_id'
    assert result['video_title'] == 'Test Video'
    assert result['channel_name'] == 'Test Channel'
    assert result['video_upload_date'] == '20230101'
    assert result['video_duration'] == 300
    assert result['view_count'] == 1000
    assert result['like_count'] == 100
    assert result['tags'] == ['tag1', 'tag2']
    assert 'processing_date' in result