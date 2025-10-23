#!/usr/bin/env python3
# netid: abespejo

import sys
from typing import List, Dict

# O(N) where N is the number of tokens in the file
def tokenize(text_file_path: str) -> List[str]:
    tokens: List[str] = []
    current: List[str] = []
    with open(text_file_path, "r", encoding="utf-8", errors="replace") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            for ch in chunk:
                if ch.isascii() and (ch.isalpha() or ch.isdigit()):
                    current.append(ch.lower())
                else:
                    if current:
                        tokens.append("".join(current))
                        current.clear()
    if current:
        tokens.append("".join(current))
    return tokens

# O(N) where N is the number of tokens in the file
def compute_word_frequencies(tokens: List[str]) -> Dict[str, int]:
    res = {}
    for token in tokens:
        if token in res:
            res[token] += 1
        else:
            res[token] = 1
    return res

# O(N log N + N) The time to sort the items + the time to print them
def print_frequencies(frequencies: Dict[str, int]) -> None:
    sorted_items = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
    for word, count in sorted_items:
        print(f"{word} = {count}")

# O(N log N) = O(N log N) where N is the number of tokens in the file
def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(1)
    file_path = args[0]
    tokenized = tokenize(file_path)
    frequencies = compute_word_frequencies(tokenized)
    print_frequencies(frequencies)

if __name__ == "__main__":
    main()
