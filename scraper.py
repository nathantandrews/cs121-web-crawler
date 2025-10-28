import re
import utils.token as tkn
import utils.report as rprt
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


def scraper(url, resp):
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
    # @TODO
    links = set()
    try:
        soup = BeautifulSoup(resp.raw_response.text, 'lxml')


        # start decomposition process:
        for tag in soup.find_all():
            if(tag == 'a'):
                href = tag['href']
            
                if not href:
                    continue
                    
                href = href.strip()
                
                if href.startswith('#') or href.lower().startswith('javascript:'):
                    continue
                    
                links.add(href)
            elif tag not in ['script', 'style', 'noscript', 'link', 'meta', 'nav', 'header', 'footer', 'aside', 'form', 'input', 'button', 'select', 'textarea', 'label', 'iframe', 'svg', 'canvas', 'template',]:
                text = tag.get_text(text)
                token.tokenize(text)
            
    except Exception as e:
        print(f"lol broke: {e}")
        return set()
        
    links = {link for link in links if is_valid(link)}

    return set(links)