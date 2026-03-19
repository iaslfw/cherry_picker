# Licensed under the MIT License.
# Copyright (c) 2026 Sebastian Wolf (iaslfw)

from src.configs.settings import Settings
from src.configs.printer import ConsolePrinter
from src.scraper.tracker import init_log
from src.scraper.download_files import download_all_files
from src.scraper.site_scraper import (
    create_authenticated_session,
    scrape_course_page,
)


def main():
    printer = ConsolePrinter()

    try:
        Settings.validate()
        init_log()
        printer.print_banner()

        session, driver = create_authenticated_session(
            Settings.LOGIN_URL, Settings.USER_NAME, Settings.PASSWORD
        )

        courses = Settings.get_courses_from_json()

        for course in courses:
            course_id, course_name = course["id"], course["name"]  # type: ignore

            printer.log(
                msg=f"[bold cyan]Processing course:[/] [yellow]{course_name}[/]"
            )

            url = f"{Settings.LOGIN_URL}/course/view.php?id={course_id}"
            scraped_data: tuple[list[str], str] = scrape_course_page(
                driver, session, url
            )

            links = scraped_data[0]
            title = scraped_data[1]

            download_all_files(printer, session, title, str(course_name), links)  # type: ignore

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
