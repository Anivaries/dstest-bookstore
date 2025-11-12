import pandas as pd
import json
import re

jsonl_file = "results_years.jsonl"
isbn_to_data = {}

with open(jsonl_file, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        isbn = item["isbn"]
        data = item.get("data", {})
        publish_date = data.get("publish_date", "")
        isbn_to_data[isbn] = {"publish_date": publish_date, }

input_csv = "BX-Book-clean_new.csv"
output_csv = "BX-Book-clean_new_new.csv"

df = pd.read_csv(input_csv, sep=';', dtype=str)


def clean_isbn(s):
    return s.strip().replace("-", "").replace(" ", "") if isinstance(s, str) else s


def extract_year(date_str):
    match = re.search(r'\b(\d{4})\b', date_str)
    if match:
        return match.group(1)
    return None


def update_row(row):
    isbn = clean_isbn(row["ISBN"])
    if isbn in isbn_to_data:
        row["Year-Of-Publication"] = extract_year(
            isbn_to_data[isbn]["publish_date"])
    return row


df = df.apply(update_row, axis=1)

df.to_csv(output_csv, sep=';', index=False, encoding='utf-8')
# print(output_csv)
