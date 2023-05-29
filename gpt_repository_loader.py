#!/usr/bin/env python3

import os
import sys
import fnmatch
import argparse

def get_ignore_list(ignore_file_path):
    ignore_list = []
    with open(ignore_file_path, 'r') as ignore_file:
        for line in ignore_file:
            if sys.platform == "win32":
                line = line.replace("/", "\\")
            ignore_list.append(line.strip())
    return ignore_list

def should_ignore(file_path, ignore_list):
    for pattern in ignore_list:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def process_repository(repo_path, ignore_list, output_file_path, input_files, splits):
    split_count = 0
    file_count = 0
    output_file = open(f"{output_file_path}_{split_count}.txt", 'w')
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(file_path, repo_path)

            if input_files and relative_file_path not in input_files:
                continue

            if not should_ignore(relative_file_path, ignore_list):
                with open(file_path, 'r', errors='ignore') as file:
                    contents = file.read()
                output_file.write("-" * 4 + "\n")
                output_file.write(f"{relative_file_path}\n")
                output_file.write(f"{contents}\n")
                file_count += 1

                if file_count >= splits:
                    output_file.write("--END--")
                    output_file.close()
                    split_count += 1
                    output_file = open(f"{output_file_path}_{split_count}.txt", 'w')
                    file_count = 0
    output_file.write("--END--")
    output_file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_path", help="/path/to/git/repository")
    parser.add_argument("-p", "--preamble", help="/path/to/preamble.txt")
    parser.add_argument("-o", "--output", help="/path/to/output_file.txt", default='output')
    parser.add_argument("-i", "--input_files", nargs='*', help="List of specific files to be included in the output file.")
    parser.add_argument("-s", "--splits", type=int, default=1, help="Number of output files.")
    args = parser.parse_args()

    repo_path = args.repo_path
    ignore_file_path = os.path.join(repo_path, ".gptignore")
    if sys.platform == "win32":
        ignore_file_path = ignore_file_path.replace("/", "\\")

    if not os.path.exists(ignore_file_path):
        # try and use the .gptignore file in the current directory as a fallback.
        HERE = os.path.dirname(os.path.abspath(__file__))
        ignore_file_path = os.path.join(HERE, ".gptignore")

    preamble_file = args.preamble
    output_file_path = args.output
    input_files = args.input_files if args.input_files else None
    splits = args.splits if args.splits else 1

    if os.path.exists(ignore_file_path):
        ignore_list = get_ignore_list(ignore_file_path)
    else:
        ignore_list = []

    process_repository(repo_path, ignore_list, output_file_path, input_files, splits)
    print(f"Repository contents written to {output_file_path}_*.txt")

