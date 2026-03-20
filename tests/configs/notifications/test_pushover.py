# type: ignore

from unittest.mock import patch
from src.configs.notifications.pushover import PushoverConfig


@patch("src.configs.notifications.pushover.Settings")
def test_pushover_initialization(mock_settings):
    """Test PushoverConfig correctly reads settings."""

    mock_settings.PUSHOVER_TOKEN = "test_token"
    mock_settings.PUSHOVER_USER_KEY = "test_user"

    pushover = PushoverConfig()

    assert pushover.token == "test_token"
    assert pushover.user_key == "test_user"
