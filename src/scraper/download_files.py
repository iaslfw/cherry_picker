import os
import signal
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

progress = Progress(
    TextColumn("[bold blue]{task.fields[file_name]}", justify="left"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
)

done_event = Event()


def handle_sigint(signum, frame):  # type: ignore
    done_event.set()


signal.signal(signal.SIGINT, handle_sigint)  # type: ignore


def _handle_file_download(
    session: requests.Session, task_id: TaskID, url: str, path: str
) -> None:
    progress.console.log(f"Requesting file: {url}")

    response = session.get(url, allow_redirects=True)  # type: ignore
    content_type = response.headers.get("Content-Type", "")

    if "text/html" in content_type:
        soup = BeautifulSoup(response.content, "html.parser")
        meta = soup.find("meta", attrs={"http-equiv": "refresh"})
        print(meta)
        progress.console.log(f"URL returned HTML, not a file: {url}")
        return

    progress.update(task_id, total=int(response.headers.get("Content-Length", 0)))
    with open(path, "wb") as dest_file:
        print(path)
        progress.start_task(task_id)
        for data in response.iter_content(chunk_size=32768):
            dest_file.write(data)
            progress.update(task_id, advance=len(data))
            if done_event.is_set():
                return

    progress.console.log(f"Finished downloading: {task_id} - {url}")


def download_files(
    urls: list[dict[str, str]], dest_dir: str, session: requests.Session
) -> None:
    """Download multiple files to the given directory."""

    with progress:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for url in urls:
                print(url)
                url, text = url["url"], url["text"]

                # file_id = url.split("/")[-1]
                dest_path = os.path.join(dest_dir, text)
                task_id = progress.add_task("download", file_name=text, start=False)
                pool.submit(_handle_file_download, session, task_id, url, dest_path)
