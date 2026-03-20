import os
import json
from pathlib import Path
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = BASE_DIR / "src" / "files"
    DOWNLOAD_DIR = DATA_DIR / "downloads"
    LOG_FILE = DATA_DIR / "download_history.csv"
    COURSES_FILE = DATA_DIR / "courses.json"

    LOGIN_URL: str | None = os.getenv("LOGIN_URL")
    USER_NAME: str | None = os.getenv("USER_NAME")
    PASSWORD: str | None = os.getenv("PASSWORD")
    PUSHOVER_TOKEN: str | None = os.getenv("PUSHOVER_TOKEN")
    PUSHOVER_USER_KEY: str | None = os.getenv("PUSHOVER_USER_KEY")
    GOOGLE_CLIENT_ID: str | None = os.getenv("GOOGLE_CLIENT_ID")

    @classmethod
    def get_courses_from_json(cls) -> List[dict[str, str | int]]:
        """Load course list from JSON file."""

        if not cls.COURSES_FILE.exists():
            return []

        with cls.COURSES_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def validate(cls):
        """Ensure all required environment variables are set."""

        missing = []
        if not cls.LOGIN_URL:
            missing.append("LOGIN_URL")  # type: ignore
        if not cls.USER_NAME:
            missing.append("USER_NAME")  # type: ignore
        if not cls.PASSWORD:
            missing.append("PASSWORD")  # type: ignore
        if not cls.PUSHOVER_TOKEN:
            missing.append("PUSHOVER_TOKEN")  # type: ignore
        if not cls.PUSHOVER_USER_KEY:
            missing.append("PUSHOVER_USER_KEY")  # type: ignore
        if not cls.GOOGLE_CLIENT_ID:
            missing.append("GOOGLE_CLIENT_ID")  # type: ignore
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"  # type: ignore
            )
