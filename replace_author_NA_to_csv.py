import pandas as pd
import json
import re

jsonl_file = "results_NA_short_publisher.jsonl"
isbn_to_data = {}

with open(jsonl_file, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        isbn = item["isbn"]
        data = item.get("data", {})
        publishers_list = data.get("publishers", [])
        publishers = ", ".join(p.get("name", "") for p in publishers_list)
        isbn_to_data[isbn] = {"publishers": publishers}

input_csv = "BX-Books-cleaned_new.csv"
output_csv = "BX-Books-clean_NEWEST.csv"

df = pd.read_csv(input_csv, sep=';', dtype=str)


def clean_isbn(s):
    return s.strip().replace("-", "").replace(" ", "") if isinstance(s, str) else s


def update_row(row):
    isbn = clean_isbn(row["ISBN"])
    if isbn in isbn_to_data:
        row["Publisher"] = isbn_to_data[isbn]["publishers"]
    return row


df = df.apply(update_row, axis=1)
df.to_csv(output_csv, sep=';', index=False, encoding='utf-8')
# print(output_csv)
