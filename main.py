# Licensed under the MIT License.
# Copyright (c) 2026 Sebastian Wolf (iaslfw)

from src.configs.notifications.pushover import PushoverConfig
from src.configs.settings import Settings
from src.configs.printer import ConsolePrinter
from src.configs.custom_types import CourseSummary
from src.scraper.tracker import init_log
from src.scraper.download_files import download_all_files
from src.scraper.site_scraper import (
    create_authenticated_session,
    scrape_course_page,
)


def main():
    printer = ConsolePrinter()
    pushover = PushoverConfig()
    scrapping_summary: list[CourseSummary] = []

    try:
        Settings.validate()
        printer.print_banner()
        init_log()

        session, driver = create_authenticated_session(
            str(Settings.LOGIN_URL),
            str(Settings.USER_NAME),
            str(Settings.PASSWORD),
        )

        course_list = Settings.get_courses_from_json()

        for course in course_list:
            course_id = int(course["id"])
            course_name = str(course["name"])

            printer.log(
                msg=f"[bold cyan]Processing course:[/] [yellow]{course_name}[/]"
            )

            url = f"{Settings.LOGIN_URL}/course/view.php?id={course_id}"
            links_found: list[str] = scrape_course_page(driver, session, url)

            scraped_data = download_all_files(
                printer,
                session,
                course_name,
                links_found,
            )
            scrapping_summary.append(scraped_data)

        pushover.send_notification(scrapping_summary)
        session.close()
        driver.quit()

    except ValueError as e:
        print(f"An error occurred:\n{e}")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting gracefully.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
