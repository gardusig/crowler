from dataclasses import dataclass
from typing import Any
import requests
from bs4 import BeautifulSoup, Tag

LINK_SKIP_PATTERNS = [
    "javascript:",
    "mailto:",
    "tel:",
    "#",
    "cookie",
    "privacy",
    "terms",
    "login",
    "signup",
]

NON_CONTENT_ELEMENTS = [
    "script",
    "style",
    "nav",
    "header",
    "footer",
    "aside",
    "noscript",
    "iframe",
    "form",
]


@dataclass
class HtmlData:
    url: str
    title: str
    meta: dict[str, Any]
    links: list[str]
    text: str


def extract_html_data(url: str) -> HtmlData:
    """
    Fetches a URL, parses its HTML, and extracts relevant data.
    Returns a dictionary with title, meta tags, links, and visible text.
    """
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    meta: dict[str, Any] = {}
    for tag in soup.find_all("meta"):
        if isinstance(tag, Tag):
            name = tag.get("name")
            property_attr = tag.get("property")
            content = tag.get("content")
            if name and content:
                key = name if isinstance(name, str) else " ".join(name)
                meta[key] = content
            elif property_attr and content:
                key = (
                    property_attr
                    if isinstance(property_attr, str)
                    else " ".join(property_attr)
                )
                meta[key] = content

    links = []
    for el in soup.find_all("a"):
        if isinstance(el, Tag):
            href = el.get("href")
            if href and isinstance(href, str):
                if not any(skip in href.lower() for skip in LINK_SKIP_PATTERNS):
                    links.append(href)

    content_soup = BeautifulSoup(str(soup), "html.parser")

    for element in content_soup(NON_CONTENT_ELEMENTS):
        element.decompose()

    text = content_soup.get_text(separator="\n", strip=True)

    return HtmlData(url=url, title=title, meta=meta, links=links, text=text)
