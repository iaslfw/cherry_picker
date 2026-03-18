import re
import requests

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from .download_files import download_files


def _extract_link_data(tags: ResultSet[Tag]) -> list[dict[str, str]]:
    """Extract the link data from the given tags."""

    anchor_links: list[dict[str, str]] = []

    for link in tags:
        link_url = str(link.get("href", ""))
        link_text = str(link.find("span", class_="instancename").getText(strip=True))  # type: ignore
        link_data: dict[str, str] = {
            "url": link_url,
            "text": link_text,
        }

        anchor_links.append(link_data)

    return anchor_links


def setup_scraper(site_data: requests.Response, session: requests.Session) -> None:
    """Initial scraper to extract resource-links from course

    Args:
        site_data (requests.Response): Information about the site to scrape, including the HTML content and status code.
            session (requests.Session): Authenticated session for subsequent requests.
    """

    if site_data.status_code == 200:
        print(f"{site_data.url}: Successfully authenticated!")
        soup = BeautifulSoup(site_data.content, "html.parser")

        page_title = soup.title.text  # type: ignore
        anchor_tags = soup.find_all(
            "a",
            href=re.compile(r"resource/view\.php\?id=\d+"),
            recursive=True,
        )

        link_data = _extract_link_data(anchor_tags)

        download_files(link_data, "src/files/downloads", session)

    else:
        print("Failed to authenticate. Please check your credentials and try again.")


# <a
#     class="aalink stretched-link"
#     href="https://moodle.dhbw.de/mod/resource/view.php?id=365725"
#     onclick=""
# >
#     <span class="instancename">
#         Probeklausur
#         <span class="accesshide">
#             Datei
#         </span>
#     </span>
# </a>
