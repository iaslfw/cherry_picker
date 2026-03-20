# type: ignore
import pytest
from unittest.mock import MagicMock, patch
from src.configs.printer import ConsolePrinter


@pytest.fixture
def printer():
    with (
        patch("src.configs.printer.Console"),
        patch("src.configs.printer.Progress"),
    ):
        return ConsolePrinter()


def test_init(printer):
    """Test initialization of ConsolePrinter"""

    assert printer.console is not None
    assert printer.progress is not None
    assert printer._is_running is False


def test_print_banner(printer):
    """Test print_banner calls console.print"""

    printer.print_banner()
    printer.console.print.assert_called_once()


def test_start_status_update(printer):
    """Test start_status_update starts the status animation"""

    mock_status = MagicMock()
    printer.console.status.return_value = mock_status

    printer.start_status_update("Scanning...")

    printer.console.status.assert_called_with("[bold green]Scanning...")
    mock_status.start.assert_called_once()
    assert printer.status == mock_status


def test_stop_status_update(printer):
    """Test stop_status_update stops the status animation and logs completion"""

    mock_status = MagicMock()
    printer.status = mock_status

    printer.stop_status_update()

    mock_status.stop.assert_called_once()
    assert printer.console.log.call_count == 2


def test_start_progress(printer):
    """Test start_progress starts the progress bar"""

    printer.start_progress()
    printer.progress.start.assert_called_once()
    assert printer._is_running is True


def test_start_progress_already_running(printer):
    """Test start_progress does nothing if already running"""

    printer._is_running = True
    printer.start_progress()
    printer.progress.start.assert_not_called()


def test_stop_progress(printer):
    """Test stop_progress stops the progress bar"""

    printer._is_running = True
    printer.stop_progress()
    printer.progress.stop.assert_called_once()
    assert printer._is_running is False


def test_stop_progress_not_running(printer):
    """Test stop_progress does nothing if not running"""

    printer._is_running = False
    printer.stop_progress()
    printer.progress.stop.assert_not_called()


def test_add_download_task(printer):
    """Test add_download_task adds a task to progress"""

    printer.progress.add_task.return_value = 1
    task_id = printer.add_download_task("test.pdf", 100)

    printer.progress.add_task.assert_called_with(
        description="test.pdf", total=100
    )
    assert task_id == 1


def test_update_download_task(printer):
    """Test update_download_task updates the progress of a task"""

    mock_task = MagicMock()
    mock_task.total = 100
    printer.progress.tasks = {1: mock_task}

    printer.update_download_task(1, 10)

    printer.progress.update.assert_called_with(1, advance=10, total=100)


def test_finish_download_task(printer):
    """Test finish_download_task completes a task and logs it"""

    mock_task = MagicMock()
    mock_task.total = 100
    printer.progress.tasks = {1: mock_task}

    printer.finish_download_task(1, "test.pdf")

    printer.console.log.assert_called_with(
        "[bold green]Downloaded:[/] test.pdf"
    )
    printer.progress.update.assert_called_with(1, completed=100)


def test_log(printer):
    """Test log calls console.log"""

    printer.log("Hello World")
    printer.console.log.assert_called_with("Hello World")
