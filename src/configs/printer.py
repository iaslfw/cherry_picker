from rich.console import Console
from rich.status import Status
from rich.progress import (
    Progress,
    TaskID,
    TextColumn,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
)


class ConsolePrinter:
    def __init__(self):
        self.console = Console()
        self.status: Status | None = None
        self.progress = Progress(
            TextColumn("[bold blue]{task.description}", justify="left"),
            BarColumn(bar_width=40),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            console=self.console,
            transient=False,
        )
        self._is_running = False

    def print_banner(self):
        self.console.print("""
            [bold magenta]Welcome to UniLooter![/]
            [bold cyan]Your tool for downloading course materials with ease.[/]
                        ⠀⠀⠀⠀⠀⠠⣤⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠈⠙⠿⣿⣿⣷⣦⡀⠀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⢿⣿⣇⠘⠿⠷⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠙⢿⣷⣤⣤⡀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⠆⠀⠙⢿⣿⣿⡄⠀⠈⣿⡟⠀⠀⢸⣿⣿⣿⠀
            ⠀⠀⠀⠀⠀⠀⠀⣠⣴⣿⠟⠁⠀⠀⠀⠈⠻⣿⣷⠀⠀⣿⠁⠀⠀⠀⣿⣿⣿⠀
            ⠀⠀⠀⠀⠀⣠⣾⣿⠟⠁⠀⠀⢠⣦⣄⠀⠀⠘⢿⡇⠀⠁⠀⠀⠀⠀⢹⣿⣿⠀
            ⠀⠀⠀⢠⣾⣿⠟⠁⠀⠀⠀⠀⠉⠙⠛⠛⠒⠀⠈⠃⠀⠀⠀⣴⣶⣾⣿⣿⣿⠀
            ⠀⢀⣴⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⠀
            ⠀⠀⠙⠁⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⡇⠀⠀⠀⠀⠸⣿⣿⣿⣿⣿⣿⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣃⠀⠀⠀⠀⠀⠀⠉⠻⣿⣿⣿⠀
            ⠀⠀⠀⠀⣤⣤⣄⣀⡀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣶⣤⡄⠀⠀⠀⣠⣿⣿⣿⠀
            ⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⢰⣿⣿⣿⣿⠀
            ⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣦⣤⣽⣿⣿⣿⠀
            ⠀⠀⠀⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠀
        """)

    def start_status_update(self, msg: str):
        self.status = self.console.status(f"[bold green]{msg}")
        self.status.start()

    def stop_status_update(self):
        if self.status:
            self.status.stop()
            self.console.log("Session setup complete")
            self.console.log("Continuing with downloading resources...")

    def start_progress(self):
        if not self._is_running:
            self.progress.start()
            self._is_running = True

    def stop_progress(self):
        if self._is_running:
            self.progress.stop()
            self._is_running = False

    def add_download_task(self, filename: str, total_size: int | None):
        """Create new download bar for given file"""
        return self.progress.add_task(description=filename, total=total_size)

    def update_download_task(self, task_id: TaskID, advance: int):
        """Update download progress for given task"""
        self.progress.update(
            task_id, advance=advance, total=self.progress.tasks[task_id].total
        )

    def finish_download_task(self, task_id: TaskID, file_name: str):
        """Update download progress for given task"""
        self.console.log(f"[bold green]Downloaded:[/] {file_name}")
        self.progress.update(
            task_id, completed=self.progress.tasks[task_id].total
        )
        # self.progress.tasks.remove(self.progress.tasks[task_id])

    def log(self, msg: str):
        self.console.log(msg)
