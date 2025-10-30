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
    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(resp.raw_response.content.decode('utf-8', errors='ignore'), 'lxml')
    soup.url = url
    links: list[str] = extract_next_links(soup)
    tokens = get_content(soup)
    return links, tokens

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlprs.urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        allowed_domains = {".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"}

        blocked_keywords = {
            "accounts",
            "home_directory",
            "calendar",
            "doku.php",  
            "tab_files", 
            "do=media", 
        }

       
        if (
            not any(parsed.netloc.endswith(domain) for domain in allowed_domains)
            or any(keyword in url for keyword in blocked_keywords)
            or re.search(const.NGS_R, parsed.netloc.lower())
            or re.search(const.GRAPE_R, parsed.netloc.lower())
            or re.search(const.MONTH_YEAR_R, parsed.path)
            or re.search(const.MSE_R, parsed.netloc.lower())
            or (re.search(const.ISG_R, parsed.netloc.lower()) and re.search(const.MONTH_YEAR_R, parsed.path))
            or re.search(const.TRIBE_BAR_R, parsed.query)
            or (re.search(const.ISG_ICS, parsed.netloc.lower()) and re.search(const.SOMETHING_SOMETHING_R, parsed.path))
            or re.search(const.IDK_20_R, parsed.path)
            or re.search(const.IDK_THIS_CAUSE_ERROR, parsed.path)
            or re.search(const.PAGNATION_R, parsed.netloc.lower() + parsed.path.lower() + parsed.query.lower())
        ):
            return False

    
        return not re.match(const.DEFAULT_INVALID_RE, parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

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