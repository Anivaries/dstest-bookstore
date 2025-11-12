import csv
import json
import time
import requests
from pathlib import Path
import pandas as pd
from typing import List
import math
import sys

INPUT_CSV = "invalid_author_NA_name.csv"
BATCH_SIZE = 50

DELAY = 1
MAX_RETRIES = 5
PROGRESS_FILE = "progress.json"
# RESULTS_FILE = "results_years.jsonl"  # used for bad years
# MISSING_FILE = "missing_years.csv"  # used for bad years
# RESULTS_FILE = "results.jsonl" #used for book title, book author, and publisher
# MISSING_FILE = "missing.csv" #used for book title, book author, and publisher
# Look for all Not Applicable author col
RESULTS_FILE = "results_NA_short_publisher.jsonl"
# Look for all Not Applicable author col
MISSING_FILE = "invalid_publisher_NA_short_name.csv"

OPENLIB_URL = "https://openlibrary.org/api/books"


def clean_isbn(s: str) -> str:
    if not s:
        return ""
    s = s.strip().replace("-", "").replace(" ", "")
    return s


def is_valid_isbn10(isbn: str) -> bool:
    if len(isbn) != 10:
        return False
    total = 0
    for i, ch in enumerate(isbn):
        if ch.upper() == "X":
            val = 10 if i == 9 else -1
        elif ch.isdigit():
            val = int(ch)
        else:
            val = -1
        if val < 0:
            return False
        total += (10 - i) * val
    return total % 11 == 0


def is_valid_isbn13(isbn: str) -> bool:
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    total = 0
    for i, ch in enumerate(isbn):
        n = int(ch)
        total += n if i % 2 == 0 else 3*n
    return total % 10 == 0


def is_valid_isbn(isbn: str) -> bool:
    s = clean_isbn(isbn)
    if len(s) == 10:
        return is_valid_isbn10(s)
    if len(s) == 13:
        return is_valid_isbn13(s)
    return False


def load_input_isbns(path: str) -> List[str]:
    isbns = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            raw = row.get('ISBN') or ""
            s = clean_isbn(raw)
            if s:
                isbns.append(s)
    return isbns


def save_progress(seen_count, idx):
    Path(PROGRESS_FILE).write_text(json.dumps(
        {"seen_count": seen_count, "idx": idx}))


def load_progress():
    p = Path(PROGRESS_FILE)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except:
            return None
    return None


def fetch_openlibrary_batch(isbns: List[str]) -> dict:
    bibkeys = ",".join(f"ISBN:{i}" for i in isbns)
    params = {"bibkeys": bibkeys, "format": "json", "jscmd": "data"}
    headers = {"User-Agent": "BulkISBNFetcher/1.0 (k0m4r4c00@gmail.com)"}
    attempt = 0
    while True:
        attempt += 1
        r = requests.get(OPENLIB_URL, params=params,
                         headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()
        r.raise_for_status()


def main():
    raw_isbns = load_input_isbns(INPUT_CSV)
    seen = set()
    isbns = []
    for s in raw_isbns:
        if s not in seen:
            seen.add(s)
            isbns.append(s)

    valid_isbns = []
    invalid_logged = []
    for s in isbns:
        if is_valid_isbn(s):
            valid_isbns.append(s)
        else:
            invalid_logged.append(s)

    results_f = open(RESULTS_FILE, "a", encoding="utf-8")
    missing_writer = csv.writer(
        open(MISSING_FILE, "a", newline='', encoding="utf-8"))

    if Path(MISSING_FILE).stat().st_size == 0:
        missing_writer.writerow(["isbn", "note"])

    prog = load_progress() or {"seen_count": 0, "idx": 0}
    start_idx = prog.get("idx", 0)

    total = len(valid_isbns)

    i = start_idx
    while i < total:
        batch = valid_isbns[i:i+BATCH_SIZE]
        try:
            data = fetch_openlibrary_batch(batch)
        except Exception as e:
            for b in batch:
                missing_writer.writerow([b, f"error: {e}"])
            i += BATCH_SIZE
            save_progress(i, i)
            time.sleep(DELAY)
            continue

        # store results per ISBN (key is 'ISBN:xxxx')
        for isbn in batch:
            key = f"ISBN:{isbn}"
            if key in data:
                out = {"isbn": isbn, "data": data[key]}
                results_f.write(json.dumps(out, ensure_ascii=False) + "\n")
            else:
                missing_writer.writerow([isbn, "not found"])
        i += BATCH_SIZE
        save_progress(i, i)
        time.sleep(DELAY)

    results_f.close()
    print("Results:", RESULTS_FILE)
    print("Missing file:", MISSING_FILE)


if __name__ == "__main__":
    main()
