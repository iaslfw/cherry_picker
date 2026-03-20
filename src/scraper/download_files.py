import re
import requests
from pathlib import Path
from rich.progress import TaskID
from src.scraper.tracker import is_already_downloaded, log_download
from src.configs.printer import ConsolePrinter
from typing import Optional
from src.configs.settings import Settings
from src.configs.custom_types import CourseSummary

course_name = ""


def download_all_files(
    printer: ConsolePrinter,
    session: requests.Session,
    course_name: str,
    links: list[str],
) -> CourseSummary:
    """Download all files from the provided links.

    Args:
        printer (ConsolePrinter): Printer instance for logging and progress updates
        session (requests.Session): Authenticated session instance
        title (str): Name of the course
        course_name (str): The name of the course for organizing downloaded files
        links (list[str]): List of file-URLs to download

    Returns:
        CourseSummary: A summary of the downloaded files for the course
    """

    course_name = _sanitize_filename(course_name)
    course_summary: CourseSummary = {
        "course_name": course_name,
        "files_downloaded": [],
    }

    if len(links) == 0:
        printer.log(
            msg=f"[dim]No files available for course:[/] [yellow]{course_name}[/]"
        )
        return course_summary
    else:
        for link in links:
            if is_already_downloaded(course_name, link):
                printer.log(msg=f"[dim]Already downloaded: {link}. Skipping")
                continue
            else:
                printer.start_progress()

                file_name = _download_file(printer, link, session, course_name)
                course_summary["files_downloaded"].append(file_name)  # type: ignore
                log_download(course_name, file_name, link)

                printer.stop_progress()

        return course_summary


# Helper functions for download_file
def _download_file(
    printer: ConsolePrinter,
    download_url: str,
    session: requests.Session,
    course_name: str,
) -> str:
    """Download file and store it within specific location.

    Args:
        printer (ConsolePrinter): Printer instance for logging and progress updates
        download_url (str): The URL of the file to download
        session (requests.Session): The authenticated session
        course_name (str): The name of the course for organizing downloaded files

    Returns:
        str: The name of the downloaded file
    """

    response = session.get(download_url, stream=True)
    response.raise_for_status()

    file_name, total_size = _extract_metadata(response, download_url)
    full_path = _get_destination_path(file_name, course_name)

    task_id = printer.add_download_task(file_name, total_size)
    printer.log(f"[dim]Starting download: {file_name}")

    try:
        _stream_response(response, str(full_path), printer, task_id)
        printer.finish_download_task(task_id, file_name)
    except Exception as e:
        printer.log(f"[bold red]Failed to save {file_name}: {e}")

    return file_name


def _sanitize_filename(filename: str) -> str:
    """Clean filename from unwanted symbols

    Args:
        filename (str): raw filename extracted from headers or URL

    Returns:
        str: cleaned filename
    """

    chars = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "Ä": "Ae",
        "Ö": "Oe",
        "Ü": "Ue",
        "ß": "ss",
    }

    for old_char, new_char in chars.items():
        filename = filename.replace(old_char, new_char)

    filename = filename.replace(" ", "_")
    filename = re.sub(r"[^\w\-_\.]", "", filename)

    return filename.lower()


def _extract_metadata(
    response: requests.Response, fallback_url: str
) -> tuple[str, int | None]:
    """Extract metadata from response headers.

    Args:
        response (requests.Response): The HTTP response object from the download request
        fallback_url (str): The URL to use for filename extraction if headers are missing
    Returns:
        tuple[str, int | None]: sanitized filename and total size (if available)
    """

    size_header = response.headers.get("Content-Length")
    total_size = int(size_header) if size_header else None

    content_disp = response.headers.get("Content-Disposition", "")
    fname_match = re.findall(r'filename="?([^";]+)"?', content_disp)

    raw_name = fname_match[0] if fname_match else fallback_url.split("/")[-1]
    return _sanitize_filename(raw_name), total_size


def _get_destination_path(
    filename: str, course_name: str, folder: Optional[Path] = None
) -> Path:
    """Ensures the directory exists and returns the full path.

    Args:
        filename (str): Filename to be stored
        course_name (str): Course name for organizing downloaded files
        folder (Optional[Path], optional): Download folder path. Defaults to Settings.DOWNLOAD_DIR.

    Returns:
        Path: Location where the file should be stored
    """

    base_folder = folder if folder else Settings.DOWNLOAD_DIR
    target_dir = base_folder / course_name.replace(" ", "_")
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / filename


def _stream_response(
    response: requests.Response,
    path: str,
    printer: ConsolePrinter,
    task_id: TaskID,
) -> None:
    """Iterates through chunks and updates the progress bar.

    Args:
        response (requests.Response): Response object containing the file stream
        path (str): Path, where files are stored
        printer (ConsolePrinter): Printer instance for logging and progress updates
        task_id (TaskID): The ID of the download task
    """

    with open(path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                printer.update_download_task(task_id, advance=len(chunk))
