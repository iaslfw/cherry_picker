from typing import TypedDict, List


class CourseSummary(TypedDict):
    course_name: str
    files_downloaded: List[str]
