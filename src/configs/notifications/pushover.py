import http.client
import urllib.parse

from src.configs.settings import Settings
from .create_message import create_message
from src.configs.custom_types import CourseSummary


class PushoverConfig:
    def __init__(self):
        self.token = Settings.PUSHOVER_TOKEN
        self.user_key = Settings.PUSHOVER_USER_KEY

    def send_notification(
        self,
        scrapping_summary: list[CourseSummary],
    ) -> None:
        """Send a Pushover notification with the download results.

        Args:
            title (str): The title of the notification
            results (dict[str, list[str]]): Dict mapping courses to their downloaded files
        """

        title, summary = create_message(scrapping_summary)
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request(
            "POST",
            "/1/messages.json",
            urllib.parse.urlencode(
                {
                    "token": self.token,
                    "user": self.user_key,
                    "message": summary,
                    "title": title,
                }
            ),
            {"Content-type": "application/x-www-form-urlencoded"},
        )

        print(conn.getresponse().read())
