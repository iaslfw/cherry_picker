import csv
from datetime import datetime
from src.configs.settings import Settings

LOG_FILE = Settings.LOG_FILE


def init_log() -> None:
    """Initializes CSV incl. header if it doesn't exist."""

    if not LOG_FILE.exists():
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Course", "Filename", "URL"])


def is_already_downloaded(course: str, url: str) -> bool:
    """Checks if a file has already been downloaded.

    Args:
        course (str): Name of the course
        url (str): URL of the file to check

    Returns:
        bool: True if the file has already been downloaded, False otherwise
    """

    if not LOG_FILE.exists():
        return False

    with LOG_FILE.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Course"] == course and row["URL"] == url:
                return True
    return False


def log_download(course: str, filename: str, url: str) -> None:
    """Logs a successful download to the CSV file.

    Args:
        course (str): Name of the course
        filename (str): Filename to be stored
        url (str): URL of the file to check
    """

    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        timestamp = datetime.now().isoformat()
        writer.writerow([timestamp, course, filename, url])
