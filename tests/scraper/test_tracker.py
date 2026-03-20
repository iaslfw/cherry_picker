# type: ignore

import csv
import pytest
from src.scraper.tracker import init_log, is_already_downloaded, log_download
import src.scraper.tracker


@pytest.fixture
def mock_log_file(tmp_path):
    log_file = tmp_path / "test_history.csv"
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(src.scraper.tracker, "LOG_FILE", log_file)
        yield log_file


def test_init_log(mock_log_file):
    """Test that init_log creates a CSV with the correct header."""

    init_log()
    assert mock_log_file.exists()

    with mock_log_file.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["Timestamp", "Course", "Filename", "URL"]


def test_is_already_downloaded(mock_log_file):
    """Test is_already_downloaded for both True and False cases."""

    assert is_already_downloaded("Course1", "http://test.com/file1") is False

    init_log()
    log_download("Course1", "file1.pdf", "http://test.com/file1")

    assert is_already_downloaded("Course1", "http://test.com/file1") is True
    assert is_already_downloaded("Course1", "http://test.com/file2") is False
    assert is_already_downloaded("Course2", "http://test.com/file1") is False


def test_log_download(mock_log_file):
    """Test that log_download appends the correct data to the CSV."""

    init_log()
    log_download("Math", "calc.pdf", "http://uni.edu/calc.pdf")

    with mock_log_file.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["Course"] == "Math"
        assert rows[0]["Filename"] == "calc.pdf"
        assert rows[0]["URL"] == "http://uni.edu/calc.pdf"
        assert "Timestamp" in rows[0]
