# type: ignore

from unittest.mock import patch
from src.configs.notifications.create_message import create_message


@patch("src.configs.notifications.create_message.Settings")
def test_create_message_with_content(mock_settings):
    """Test message creation with valid courses and files."""

    test_data = [
        {
            "course_name": "AI Course",
            "files_downloaded": ["lecture1.pdf", "lab1.ipynb"],
        },
        {"course_name": "Management", "files_downloaded": ["skript.pdf"]},
    ]

    title, message = create_message(test_data)

    assert title == "Finished picking cherries of 2 Trees"
    assert "Scraped 2 courses" in message or "scrapping 2 courses" in message
    assert "3 files in total" in message
    assert "AI Course:" in message
    assert "- lecture1.pdf" in message
    assert "- lab1.ipynb" in message
    assert "Management:" in message
    assert "- skript.pdf" in message


@patch("src.configs.notifications.create_message.Settings")
def test_create_message_empty(mock_settings):
    """Test message creation with no new files."""

    test_data = [
        {"course_name": "AI Course", "files_downloaded": []},
        {"course_name": "Management", "files_downloaded": []},
    ]

    title, message = create_message(test_data)

    assert "2 Trees" in title
    assert "0 files" in message
    assert "Destination:" in message
    assert "AI Course:" in message
    assert "No new files found." in message
