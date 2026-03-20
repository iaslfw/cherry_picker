# type: ignore
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
from src.scraper.download_files import (
    _sanitize_filename,
    _extract_metadata,
    _get_destination_path,
    _stream_response,
    _download_file,
    download_all_files,
)


def test_sanitize_filename():
    """Test filename sanitization for various edge cases."""
    assert _sanitize_filename("test file.pdf") == "test_file.pdf"
    assert _sanitize_filename("München.pdf") == "muenchen.pdf"
    assert _sanitize_filename("Äöüß.pdf") == "aeoeuess.pdf"
    assert _sanitize_filename("file#@%!.txt") == "file.txt"


@patch("src.scraper.download_files._sanitize_filename")
def test_extract_metadata(mock_sanitize):
    """Test metadata extraction from response headers."""

    mock_sanitize.side_effect = lambda x: x

    response_cd = MagicMock()
    response_cd.headers = {
        "Content-Length": "100",
        "Content-Disposition": 'attachment; filename="report.pdf"',
    }
    fname, size = _extract_metadata(response_cd, "http://test.com/something")
    assert fname == "report.pdf"
    assert size == 100

    response_no_cd = MagicMock()
    response_no_cd.headers = {"Content-Length": "200"}
    fname, size = _extract_metadata(response_no_cd, "http://test.com/notes.txt")
    assert fname == "notes.txt"
    assert size == 200
    mock_sanitize.assert_called()


@patch("src.scraper.download_files.Settings")
def test_get_destination_path(mock_settings, tmp_path):
    """Test destination path creation."""
    mock_settings.DOWNLOAD_DIR = tmp_path
    fname = "test.pdf"
    course = "AI Course"

    dest = _get_destination_path(fname, course)

    expected_dir = tmp_path / "AI_Course"
    assert dest == expected_dir / "test.pdf"
    assert expected_dir.exists()


def test_stream_response():
    """Test streaming response to file with progress updates."""

    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]

    mock_printer = MagicMock()
    task_id = 1

    m = mock_open()
    with patch("builtins.open", m):
        _stream_response(mock_response, "test.path", mock_printer, task_id)

    m().write.assert_any_call(b"chunk1")
    m().write.assert_any_call(b"chunk2")
    assert mock_printer.update_download_task.call_count == 2


@patch("src.scraper.download_files._stream_response")
@patch("src.scraper.download_files._get_destination_path")
@patch("src.scraper.download_files._extract_metadata")
def test_download_file(mock_extract, mock_dest, mock_stream):
    """Test the complete download flow for a single file."""

    mock_extract.return_value = ("test.pdf", 1000)
    mock_dest.return_value = Path("test_dir/test.pdf")

    mock_printer = MagicMock()
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_session.get.return_value = mock_response

    result = _download_file(
        mock_printer, "http://test.com", mock_session, "Course"
    )

    assert result == "test.pdf"
    mock_printer.add_download_task.assert_called_with("test.pdf", 1000)
    mock_stream.assert_called_once()
    mock_printer.finish_download_task.assert_called_once()


@patch("src.scraper.download_files.log_download")
@patch("src.scraper.download_files._download_file")
@patch("src.scraper.download_files.is_already_downloaded")
def test_download_all_files(mock_check, mock_download, mock_log):
    """Test downloading multiple files with skipping of already downloaded ones."""

    mock_printer = MagicMock()
    mock_session = MagicMock()

    links = ["http://link1", "http://link2"]
    mock_check.side_effect = [True, False]
    mock_download.return_value = "file2.pdf"
    result = download_all_files(mock_printer, mock_session, "MockCourse", links)

    mock_printer.log.assert_called_with(
        msg="[dim]Already downloaded: http://link1. Skipping"
    )

    assert result == {
        "course_name": "mockcourse",
        "files_downloaded": ["file2.pdf"],
    }
    assert mock_download.call_count == 1
    assert mock_printer.start_progress.call_count == 1
    assert mock_printer.stop_progress.call_count == 1
    mock_log.assert_called_once_with("mockcourse", "file2.pdf", "http://link2")
