import utils.token as tkn
import utils.report as rprt
import utils.constants as const
import utils.log as log

import urllib.parse as urlprs
import bs4
import re

LOG_DIR = "Logs"
logger = log.setup_logger(LOG_DIR)

def scraper(url, resp) -> list[str]:
    if not is_resp_valid(resp):
        return []
    links, tokens = scrape_page(url, resp)
    rprt.Report().add_page(url, tokens)
    rprt.Report().print_report()

    return links

def is_resp_valid(resp) -> bool:
    return (
        resp 
        and hasattr(resp, "raw_response")
        and getattr(resp.raw_response, "content", None)
        and resp.status == 200
    )

def scrape_page(url: str, resp) -> tuple[set[str], list[str]]:
    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(resp.raw_response.content, 'lxml')
    soup.url = url
    links: list[str] = extract_next_links(soup)
    tokens = get_content(soup)
    return links, tokens

def is_valid(url: str) -> bool:
    try:
        parsed_url: urlprs.ParseResult = urlprs.urlparse(url)
        path = parsed_url.path.lower()
        return (
            parsed_url.scheme in set(["http", "https"])
            and re.match(const.VALID_DOMAINS_RE, parsed_url.netloc.lower())
            and not re.match(const.DEFAULT_INVALID_EXTENSIONS_RE, path)
            and not re.match(const.INVALID_EXTENSIONS_RE, path)
            and not re.search(const.CALENDAR_TRAP_REGEX, parsed_url.query)
            and not re.search(const.WIKI_TRAP_RE, path)
            and not re.search(const.REPEATED_DIR_TRAP_RE, path)
            and not re.search(const.EDIT_FILE_TRAP_RE, path)
            and not re.search(const.MEDIA_FILE_TRAP_RE, path)
            and not re.search(const.EPPSTEIN_PIX_RE, path)
            and not re.search(const.EVENTS_RE, path)
            and not re.search(const.NGS_RE, parsed_url.hostname)
            and not re.search(const.DOKU_RE, parsed_url.path)
        )
    except Exception as e:
        logger.error(f"[is_valid] Error determining validity of {url}: {type(e).__name__} - {e}")
        return False

def extract_next_links(soup: bs4.BeautifulSoup) -> list[str]:
    links = set()
    try:
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            href = urlprs.urljoin(soup.url, href)
            href, _ = urlprs.urldefrag(href)
            if is_valid(href):
                links.add(href)

    except Exception as e:
        logger.error(f"[extract_next_links] Error processing {soup.url}: {type(e).__name__} - {e}")
        return list(links)

    return list(links)

def get_content(soup: bs4.BeautifulSoup) -> list[str]:
    tokens = []
    try:
        for tag in soup.find_all():
            if tag.name not in const.INVALID_TAGS:
                text = tag.get_text(strip=True)
                if text:
                    tokens.extend(tkn.tokenize(text))
        return tokens
    except Exception as e:
        logger.error(f"[get_content] Error processing {soup.url}: {type(e).__name__} - {e}")
        return []