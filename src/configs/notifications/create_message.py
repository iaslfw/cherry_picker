from src.configs.custom_types import CourseSummary
from src.configs.settings import Settings


def create_message(summary: list[CourseSummary]) -> tuple[str, str | list[str]]:
    """Create a formatted message for Pushover notification.

    Args:
        results (list[CourseSummary]): List of course summaries

    Returns:
        tuple[str, str | list[str]]: Formatted message and title
    """

    files_total = 0
    courses_total = len(summary)
    course_details = ""

    for course in summary:
        course_name = course["course_name"]
        files = course["files_downloaded"]

        files_total += len(files)

        if files_total == 0:
            course_details += f"{course_name}:\n No new files found.\n\n"
            continue
        else:
            course_details += f"{course_name}:\n"
            for file in files:
                course_details += f"- {file}\n"
            course_details += "\n"

    title = f"Finished picking cherries of {courses_total} Trees"
    summary = (
        f"Finished scrapping {courses_total} courses. Found and downloaded {files_total} files in total.\n"
        f"Destination: {Settings.DOWNLOAD_DIR}\n\n"
        f"{course_details}"
    )  # type: ignore

    return title, str(summary)
