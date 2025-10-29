import re
import utils.token as tkn
import utils.report as rprt
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

INVALID_TAGS = {'script', 'style', 'noscript', 'link', \
'meta', 'nav', 'header', 'footer', 'aside', 'form', 'input',\
 'button', 'select', 'textarea', 'label', 'iframe', 'svg', 'canvas', 'template'}

def scraper(url, resp):
    if (resp and resp.raw_response):
        text = count_50(resp)
        print(tokens)
    else:
        print("bad", resp)
    return extract_next_links(url, resp)

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        default_invalid_re = r".*\.(php|css|js|bmp|gif|jpe?g|ico" \
        + r"|png|tiff?|mid|mp2|mp3|mp4" \
        + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
        + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names" \
        + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso" \
        + r"|epub|dll|cnf|tgz|sha1" \
        + r"|thmx|mso|arff|rtf|jar|csv" \
        + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$"
        
        # Fixed: (.*\.)? makes subdomain optional, matches both ics.uci.edu and www.ics.uci.edu
        valid_domains_re = r"^(.*\.)?(ics|cs|informatics|stat)\.uci\.edu$"
        
        # Regex to check the parsed URL for calendar traps by analyzing dates in the path
        CALENDAR_TRAP_REGEX = r'(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{4}[-/]\d{1,2}|(?:date|month|year|calendar|event)[-_]?\w*=\d+|tribe[-_]bar[-_]date|ical=\d+|(?:next|prev)(?:_|-)?(?:month|year|day))'
        if re.search(CALENDAR_TRAP_REGEX, parsed.query): # check YYYY/MM or YYYY-MM pattern
            return False

        return (not re.match(default_invalid_re, parsed.path.lower())) and \
        re.match(valid_domains_re, parsed.netloc.lower())
    except TypeError:
        print ("TypeError for ", parsed)
        raise

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    links = set()
    try:
        if not resp or not hasattr(resp, "raw_response") or not \
        resp.raw_response or not resp.raw_response.content or resp.status != 200:
            return []
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')
        tokens = []
        # find links
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            href = urljoin(url, href)
            if is_valid(href):
                links.add(href)
        # get content
        for tag in soup.find_all():
            if tag.name not in INVALID_TAGS:
                text = tag.get_text(strip=True)
                if text:
                    tokens.extend(tkn.tokenize(text))
        # add to report
        rprt.Report().add_page(url, tokens)
        rprt.Report().print_report()

    except Exception as e:
        print(f"[extract_next_links] Error processing {url}: {type(e).__name__} - {e}")
        return []

    return list(links)

def extract_visible_text(resp):
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    for script in soup(["script", "style"]):
        script.decompose()
    visible_text = soup.get_text(separator=" ", strip=True)
    return re.sub(r'\s+', ' ', visible_text)

def count_50(resp):
    text = extract_visible_text(resp)
    tokens = tkn.get_tokens_set(text)
    return text
    