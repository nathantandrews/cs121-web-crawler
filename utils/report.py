import threading
import tldextract
from urllib.parse import urlparse, urlunparse
from collections import defaultdict

class Report:
    _instance = None
    def __new__(self):
        if self._instance is None:
            self._instance = super(Report, self).__new__(self)
            self.pages_dict: dict[str, int] = dict()
            self.lock = threading.lock()
        return self._instance

    def add_page(self, url: str, word_count: int) -> None:
        """Adds a page to the pages dict
        Args:
            url (str): The URL of the page to add. Assumes the fragment isn't discarded.
            word_count (int): The total words on a page.
        """
        with self.lock:
            parsed_url = urlparse(url)._replace(fragment="")
            url_no_fragment = urlunparse(modified_parsed_url)
            self.pages_dict[url_no_fragment] = word_count
    
    def get_unique_pages(self) -> set[str]:
        """Retrieves a set of unique visited pages."""
        with self.lock:
            return set(self.pages_dict.keys())
    
    def get_longest_page(self) -> str:
        """Compares all visited pages and determines the longest page."""
        with self.lock:
            return max(self.pages_dict, key=self.pages_dict.get)
    
    def get_subdomain_count(self) -> dict[str, int]:
        """Examines all unique visited pages calculates subdomain statistics.
        Returns:
            dict[str, int]: A dictionary representing subdomains and unique pages per subdomain.
        """
        with self.lock:
            subdomain_dict = defaultdict(int)
            for page in self.get_unique_pages():
                extracted_url = tldextract.extract(page)
                subdomain_dict[extracted_url.subdomain] += 1
            return subdomain_dict