import re
import requests
from typing import Any
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
from src.configs.printer import ConsolePrinter

printer = ConsolePrinter()


def create_authenticated_session(
    url: str, username: str, password: str
) -> tuple[requests.Session, WebDriver]:
    """Create authenticated session on webpage.

    Args:
        url (str): The URL of the login page.
        username (str): The username for authentication.
        password (str): The password for authentication.

    Returns:
        tuple[requests.Session, WebDriver]: A tuple containing the authenticated session and the WebDriver instance.
    """

    printer.start_status_update(msg="Setting up Session")
    session = requests.Session()
    driver = _setup_driver()

    try:
        _handle_login(driver, url, username, password)

        cookies, user_agent = _extract_metadata(driver)  # type: ignore

        for cookie in cookies:  # type: ignore
            session.cookies.set(cookie["name"], cookie["value"])  # type: ignore

        session.headers.update({"User-Agent": user_agent})
        printer.stop_status_update()

        return session, driver

    except Exception:
        if driver:
            driver.quit()
        printer.stop_status_update()
        raise


def scrape_course_page(
    driver: WebDriver, session: requests.Session, url: str
) -> list[str]:
    """Scrape current page for downloadable links containing ressources.

    Args:
        driver (WebDriver): The WebDriver instance
        session (requests.Session): The authenticated session
        url (str): The URL of the course page to scrape

    Returns:
        list[str]: A list of downloadable links
    """

    printer.log(msg=f"[dim]Scraping:[/] [bold magenta]{url}")
    try:
        driver.get(url)

        response = session.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        links = _extract_links(soup)

        return links

    except requests.exceptions.RequestException as e:
        printer.log(f"[bold red]Failed to retrieve the course page:[/] {e}")
        return []
    except Exception as e:
        printer.log(f"[bold red]An error occurred while scraping:[/] {e}")
        return []


def _setup_driver() -> WebDriver:
    """Setup Selenium WebDriver

    Returns:
        WebDriver: Freshly created WebDriver instance.

    Raises:
        WebDriverException: If the browser cannot be started.
    """
    printer.log(msg="Setting up WebDriver")

    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = WebDriver(options=options)
        return driver
    except WebDriverException as e:
        printer.log(f"[bold red]Failed to start Chrome/ChromeDriver:[/] {e}")
        raise


def _extract_metadata(driver: WebDriver) -> tuple[Any, Any]:
    """Extract meta-data from authenticated session

     Args:
        driver (WebDriver): WebDriver instance of authenticated session.

    Returns:
        tuple[Any, Any]: Tuple containing the extracted cookies and user agent.
    """

    try:
        printer.log(msg="Extracting session metadata")
        cookies = driver.get_cookies()  # type: ignore
        user_agent = driver.execute_script("return navigator.userAgent")  # type: ignore
        return cookies, user_agent  # type: ignore

    except Exception as e:
        printer.log(f"[bold red]Failed to extract session metadata:[/] {e}")
        raise


def _handle_login(
    driver: WebDriver, url: str, username: str, password: str
) -> None:
    """Handle the Moodle login flow with explicit waits."""

    printer.log(msg="Handling login")
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)

        student_button = wait.until(
            EC.element_to_be_clickable((By.ID, "button-Student"))
        )
        student_button.click()

        username_field = wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys(username)

        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)

        submit_button = driver.find_element(By.ID, "submit_button")
        submit_button.click()

    except TimeoutException:
        printer.log(
            "[bold red]Login timed out:[/] Element not found within 20s. Check your internet or if the portal UI changed."
        )
        raise
    except NoSuchElementException as e:
        printer.log(
            f"[bold red]Login failed:[/] Could not find expected element. {e}"
        )
        raise
    except Exception as e:
        printer.log(f"[bold red]Unexpected error during login:[/] {e}")
        raise


def _extract_links(soup: BeautifulSoup) -> list[str]:
    """Extract resource links from page"""
    printer.log(msg="Extracting resource links from page")
    links: list[str] = []
    anchor_tags = soup.find_all(
        "a",
        href=re.compile(r"resource/view\.php\?id=\d+"),
        recursive=True,
    )

    for link in anchor_tags:
        link_url = str(link.get("href", ""))
        links.append(link_url)

    return links
