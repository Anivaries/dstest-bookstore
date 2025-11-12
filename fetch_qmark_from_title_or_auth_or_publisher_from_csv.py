import pandas as pd

input_file = "BX-Books-cleaned_new.csv"
output_file = "invalid_publisher_NA_short_name.csv"

df = pd.read_csv(input_file, sep=';', dtype=str)

# bad_symbols = ['�']
# bad_symbols = ['Not Applicable']
bad_symbols = ['Not Avail']

# mask = df['Book-Title'].astype(str).apply(lambda x: any(sym in x for sym in bad_symbols)) | \
#     df['Book-Author'].astype(str).apply(
#         lambda x: any(sym in x for sym in bad_symbols)) | df['Publisher'].astype(str).apply(
#         lambda x: any(sym in x for sym in bad_symbols))

mask = df['Book-Author'].astype(str).apply(lambda x: any(sym in x for sym in bad_symbols)) | df['Publisher'].astype(str).apply(
    lambda x: any(sym in x for sym in bad_symbols))

broken_rows = df[mask]

broken_rows.to_csv(output_file, index=False, sep=';')
print(f"Found {len(broken_rows)} rows with broken symbols.")
