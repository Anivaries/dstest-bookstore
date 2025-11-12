import pandas as pd
import re

input_csv = "BX-Book-clean_new_new.csv"
output_file = "invalid_years-1.csv"

df = pd.read_csv(input_csv, sep=';', dtype=str)

pattern = r'^\d{4}$'

invalid_mask = ~df['Year-Of-Publication'].astype(str).str.match(pattern)

invalid_years = df[invalid_mask]

invalid_years.to_csv(output_file, index=False, sep=';')

print(
    f"{len(invalid_years)} invalid years")
