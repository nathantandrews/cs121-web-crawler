import utils.token as tkn
import utils.report as rprt
import utils.constants as const
import utils.log as log

from urllib.parse import urlparse, urljoin, ParseResult
from bs4 import BeautifulSoup
import re

LOG_DIR = "Logs"
logger = log.setup_logger(LOG_DIR)

def scraper(url, resp):
    if not is_resp_valid(resp):
        return []
    return extract_next_links(url, resp)

def is_valid(url):
    try:
        parsed_url: ParseResult = urlparse(url)

        # check http / https (default)
        # check basic extensions (default)
        # check valid domains
        # check YYYY/MM or YYYY-MM pattern
        return parsed_url.scheme in set(["http", "https"]) and \
        not re.match(const.DEFAULT_INVALID_RE, parsed_url.path.lower()) and \
            re.match(const.VALID_DOMAINS_RE, parsed_url.netloc.lower()) and \
        not re.search(const.CALENDAR_TRAP_REGEX, parsed_url.query)
    except Exception as e:
        logger.error(f"[is_valid] Error determining validity of {url}: {type(e).__name__} - {e}")
        raise

def extract_next_links(url, resp):
    links = set()
    try:
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')
        tokens = []
        # find links
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            href = urljoin(url, href)
            if href == url:
                continue
            if is_valid(href):
                links.add(href)
        # get content
        for tag in soup.find_all():
            if tag.name not in const.INVALID_TAGS:
                text = tag.get_text(strip=True)
                if text:
                    tokens.extend(tkn.tokenize(text))
        # add to report
        rprt.Report().add_page(url, tokens)
        rprt.Report().print_report()

    except Exception as e:
        logger.error(f"[extract_next_links] Error processing {url}: {type(e).__name__} - {e}")
        return []

    return list(links)

def is_resp_valid(resp):
    if not resp or not hasattr(resp, "raw_response") or not \
    resp.raw_response or not resp.raw_response.content or resp.status != 200:
        return False
    return True

### UNCOMPLETE

# see # get content
def extract_visible_text(resp):
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    for script in soup(["script", "style"]):
        script.decompose()
    visible_text = soup.get_text(separator=" ", strip=True)
    return re.sub(r'\s+', ' ', visible_text)

# this is done in the report object btw, 
# implemented counter internally for quick aggregation
def count_50(resp):
    text = extract_visible_text(resp)
    tokens = tkn.get_tokens_set(text)
    return text
    