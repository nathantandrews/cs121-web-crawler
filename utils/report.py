import utils.token as tkn
import utils.constants as const

import os
import threading
import tldextract
from urllib.parse import urlparse, urlunparse
from collections import defaultdict, Counter

MOST_COMMON_COUNT = 50

class Report:
    pgs_tcount_dict: dict
    token_counter: Counter
    lock: threading.Lock
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Report, cls).__new__(cls)
            cls._instance.pgs_tcount_dict = dict()
            cls._instance.token_counter = Counter()
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
            self.pgs_tcount_dict[url_no_fragment] = len(tokens)
            self.token_counter.update(filter(lambda x: x not in const.STOP_WORDS, tokens))
    
    def get_unique_pages(self) -> set[str]:
        """Retrieves a set of unique visited pages."""
        with self.lock:
            return set(self.pgs_tcount_dict.keys())
    
    def get_longest_page(self) -> str:
        """Compares all visited pages and determines the longest page."""
        with self.lock:
            url = max(self.pgs_tcount_dict, key=self.pgs_tcount_dict.get)
            return (url, self.pgs_tcount_dict[url])
    
    def get_most_common_words(self, quantity: int) -> list[tuple[str, int]]:
        """Tallies up the most common words."""
        with self.lock:
            return self.token_counter.most_common(quantity)
    
    def get_subdomain_count(self) -> dict[str, int]:
        """Counts unique pages per subdomain."""
        with self.lock:
            subdomain_dict = defaultdict(int)
            for page in self.pgs_tcount_dict.keys():
                extracted_url = tldextract.extract(page)
                # Combine subdomain + domain to get a full identifier
                full_domain = ".".join(part for part in \
                                       [extracted_url.subdomain, \
                                        extracted_url.domain, \
                                            extracted_url.suffix] if part)
                subdomain_dict[full_domain] += 1
            return dict(subdomain_dict)

    
    def print_report(self):
        """Writes crawler report."""
        os.makedirs("Logs/_report", exist_ok=True)
        try:
            with open("Logs/_report/unique_pages.txt", "w") as f:
                unique_pages = self.get_unique_pages()
                f.write(f"unique pagecount: {len(unique_pages)}\n")
                for page in unique_pages:
                    f.write(f"{page}\n")

            longest_url, longest_len = self.get_longest_page()
            with open("Logs/_report/longest_page.txt", "w") as f:
                f.write(f"The longest page's url: {longest_url} ({longest_len} tokens)\n")

            with open("Logs/_report/most_common_words.txt", "w") as f:
                f.write(f"Top {MOST_COMMON_COUNT} Words:\n")
                for word_count_tup in self.get_most_common_words(MOST_COMMON_COUNT):
                    f.write(f"{word_count_tup[0]}: {word_count_tup[1]}\n")

            with open("Logs/_report/subdomain_count.txt", "w") as f:
                subdomains = self.get_subdomain_count()
                f.write(f"Subdomains and the amount of pages in each subdomain:\n")
                for sub, count in sorted(subdomains.items()):
                    f.write(f"{sub}, {count}\n")

        except Exception as e:
            print(f"[Report] Error while writing report files: {type(e).__name__} - {e}")

rprt = Report()