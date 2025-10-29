import utils.token as tkn
import utils.stopwords as stp

import os
import threading
import tldextract
from urllib.parse import urlparse, urlunparse
from collections import defaultdict

class Report:
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Report, cls).__new__(cls)
            cls._instance.pages_dict = dict()
            cls._instance.tokens = list()
            cls._instance.lock = threading.Lock()
        return cls._instance

    def add_page(self, url: str, tokens: list[str]) -> None:
        """Adds a page to the pages dict
        Args:
            url (str): The URL of the page to add. Assumes the fragment isn't discarded.
            tokens (list[str]): All of the tokens on a page.
        """
        with self.lock:
            modified_parsed_url = urlparse(url)._replace(fragment="")
            url_no_fragment = urlunparse(modified_parsed_url)
            self.tokens.extend(tokens)
            self.pages_dict[url_no_fragment] = len(tokens)
    
    def get_unique_pages(self) -> int:
        """Retrieves a set of unique visited pages."""
        with self.lock:
            return len(self.pages_dict)
    
    def get_longest_page(self) -> str:
        """Compares all visited pages and determines the longest page."""
        with self.lock:
            url = max(self.pages_dict, key=self.pages_dict.get)
            return (url, self.pages_dict[url])
    
    def get_most_common_words(self, quantity: int) -> dict[str, int]:
        with self.lock:
            frequencies = tkn.compute_word_frequencies(self.tokens)
            sorted_items = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
            non_stop_words = dict()

            return frequencies 
            
    def get_subdomain_count(self) -> dict[str, int]:
        """Counts unique pages per subdomain."""
        with self.lock:
            subdomain_dict = defaultdict(int)
            for page in self.pages_dict.keys():
                extracted_url = tldextract.extract(page)
                # Combine subdomain + domain to get a full identifier
                full_domain = ".".join(part for part in [extracted_url.subdomain, extracted_url.domain, extracted_url.suffix] if part)
                subdomain_dict[full_domain] += 1
            return dict(subdomain_dict)

    
    def print_report(self):
        """Writes crawler report."""
        os.makedirs("report", exist_ok=True)
        try:
            with open("report/unique_pages.txt", "w") as f:
                f.write(f"{self.get_unique_pages()}\n")

            longest_url, longest_len = self.get_longest_page()
            with open("report/longest_page.txt", "w") as f:
                f.write(f"{longest_url} ({longest_len} tokens)\n")

            with open("report/most_common_words.txt", "w") as f:
                for word, count in self.get_most_common_words(50).items():
                    f.write(f"{word}: {count}\n")

            with open("report/subdomain_count.txt", "w") as f:
                subdomains = self.get_subdomain_count()
                for sub, count in sorted(subdomains.items()):
                    f.write(f"{sub}, {count}\n")

        except Exception as e:
            print(f"[Report] Error while writing report files: {type(e).__name__} - {e}")

rprt = Report()