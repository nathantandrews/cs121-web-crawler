#!/usr/bin/env python3
# netid: abespejo

import sys
from typing import Set
from PartA import tokenize

# O(N) where the N is the number of unique tokens in both files 
def get_tokens_set(text_file_path: str) -> Set[str]:
    return set(tokenize(text_file_path))

# O(M + N) where M and N are the number of unique tokens in file1 and file2 respectively
def count_common_tokens(file1_path: str, file2_path: str) -> int:
    tokens_file1 = get_tokens_set(file1_path)
    tokens_file2 = get_tokens_set(file2_path)
    
    common_tokens = tokens_file1.intersection(tokens_file2)
    
    return len(common_tokens)
# O(M + N) where M and N are the number of unique tokens in file1 and file2 respectively
def main():
    if len(sys.argv) != 3:
        sys.exit(1)
    
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    
    common_count = count_common_tokens(file1_path, file2_path)
    
    print(common_count)

if __name__ == "__main__":
    main()
