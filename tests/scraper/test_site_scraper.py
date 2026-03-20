# type: ignore
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup
from src.scraper.site_scraper import (
    create_authenticated_session,
    scrape_course_page,
    _setup_driver,
    _extract_metadata,
    _handle_login,
    _extract_links,
)


@patch("src.scraper.site_scraper.WebDriver")
@patch("src.scraper.site_scraper.Options")
def test_setup_driver(mock_options, mock_webdriver):
    """Test Selenium driver setup."""
    driver = _setup_driver()
    assert driver is not None
    mock_webdriver.assert_called_once()
    args, kwargs = mock_options.return_value.add_argument.call_args_list[0]
    assert "--headless" in args


def test_extract_metadata_scraper():
    """Test extracting cookies and user agent from WebDriver."""

    mock_driver = MagicMock()
    mock_driver.get_cookies.return_value = [{"name": "test", "value": "val"}]
    mock_driver.execute_script.return_value = "Mozilla/5.0"

    cookies, ua = _extract_metadata(mock_driver)
    assert cookies == [{"name": "test", "value": "val"}]
    assert ua == "Mozilla/5.0"


@patch("src.scraper.site_scraper.WebDriverWait")
def test_handle_login(mock_wait):
    """Test the login process with explicit waits."""

    mock_driver = MagicMock()
    mock_wait.return_value.until.return_value = (
        MagicMock()
    )  # Mock the student button

    _handle_login(mock_driver, "http://login.com", "user", "pass")

    mock_driver.get.assert_called_with("http://login.com")
    assert (
        mock_driver.find_element.call_count >= 2
    )  # Password and submit button


def test_extract_links():
    """Test extraction of resource links from HTML content."""

    html = """
    <html>
        <body>
            <a href="https://moodle.uni.edu/resource/view.php?id=123">File 1</a>
            <a href="https://moodle.uni.edu/resource/view.php?id=456">File 2</a>
            <a href="https://moodle.uni.edu/other/page.php">Not a resource</a>
        </body>
    </html>
    """

    soup = BeautifulSoup(html, "html.parser")
    links = _extract_links(soup)

    assert len(links) == 2
    assert "id=123" in links[0]
    assert "id=456" in links[1]


@patch("src.scraper.site_scraper._extract_links")
def test_scrape_course_page(mock_links):
    """Test scraping a course page for links and title."""

    mock_links.return_value = ["link1", "link2"]

    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "<html><title>Test Course</title></html>"
    mock_session.get.return_value = mock_response

    links = scrape_course_page(mock_driver, mock_session, "http://course.com")

    assert links == ["link1", "link2"]
    mock_driver.get.assert_called_once_with("http://course.com")


@patch("src.scraper.site_scraper._setup_driver")
@patch("src.scraper.site_scraper._handle_login")
@patch("src.scraper.site_scraper._extract_metadata")
@patch("src.scraper.site_scraper.requests.Session")
def test_create_authenticated_session(
    mock_session_class, mock_extract, mock_login, mock_setup
):
    """Test the full flow of creating an authenticated session."""

    mock_setup.return_value = MagicMock()
    mock_extract.return_value = ([{"name": "c1", "value": "v1"}], "UserAgent")
    mock_session = mock_session_class.return_value
    mock_session.headers = {}

    session, driver = create_authenticated_session("url", "user", "pass")

    assert driver == mock_setup.return_value
    mock_login.assert_called_once()
    mock_session.cookies.set.assert_called_with("c1", "v1")
    assert mock_session.headers["User-Agent"] == "UserAgent"
