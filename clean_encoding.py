import csv
import os
import re
import html
from collections import Counter


def clean_title_formatting(text):
    """Clean escaped quotes, backslashes, and excessive double quotes from titles."""
    if not isinstance(text, str):
        return text

    # 5. Remove extra spaces around punctuation
    text = re.sub(r'\s+([,:;.!?])', r'\1', text)
    text = re.sub(r'\s{2,}', ' ', text)

    return text.strip()


# --- Expanded replacements (Western European + common double-encoded patterns) ---
replacements = {
    # --- common single-layer mojibake ---
    "Ã¤": "ä", "Ã„": "Ä",
    "Ã¶": "ö", "Ã–": "Ö",
    "Ã¼": "ü", "Ãœ": "Ü",
    "ÃŸ": "ß",
    "Ã¡": "á", "Ã©": "é", "Ã¨": "è", "Ãê": "ê", "Ãª": "ê",
    "Ã²": "ò", "Ã´": "ô", "Ã»": "û", "Ã®": "î",
    "Ã±": "ñ", "Ã‘": "Ñ",

    # --- smart quotes, dashes, ellipsis, currency ---
    "â€œ": "“", "â€\x9d": "”", "â€\x98": "‘", "â€™": "’",
    "â€“": "–", "â€”": "—", "â€¦": "…", "â‚¬": "€", "â„¢": "™",
    "Â ": "",  # stray NBSP marker sometimes appears as Â

    # --- double-encoded UTF-8 sequences ---
    "Ã?Â¤": "ä", "Ã?Â¶": "ö", "Ã?Â¼": "ü", "Ã?ÂŸ": "ß",
    "Ã?Â„": "Ä", "Ã?Â–": "Ö", "Ã?Âœ": "Ü",
    "Ã?Â¡": "á", "Ã?Â©": "é", "Ã?Â¨": "è", "Ã?Âª": "ê",
    "Ã?Â±": "ñ", "Ã?Â‘": "Ñ",

    # --- fallback patterns ---
    "Ã?¤": "ä", "Ã?¶": "ö", "Ã?¼": "ü", "Ã?Ÿ": "ß",
    "?¤": "ä", "?¶": "ö", "?¼": "ü", "?Ÿ": "ß",

    # --- triple-encoded sequences like SchuÃƒ?Ã‚?angst ---
    "ÃƒÂ¤": "ä", "ÃƒÂ¶": "ö", "ÃƒÂ¼": "ü", "ÃƒÅ“": "Ü", "ÃƒÆ’": "Ä",
    "ÃƒÂŸ": "ß",
    "ÃƒÂ¡": "á", "ÃƒÂ©": "é", "ÃƒÂ¨": "è", "ÃƒÂª": "ê",
    "ÃƒÂ±": "ñ", "Ãƒâ€“": "Ö", "Ãƒâ€ž": "Ä", "ÃƒÂœ": "Ü",
}

_sorted_bad_patterns = sorted(replacements.keys(), key=len, reverse=True)
_combined_pattern = re.compile("|".join(re.escape(k)
                               for k in _sorted_bad_patterns))


def apply_manual_replacements(text):
    """Apply a cascade of manual replacements using the replacements dict."""
    if not isinstance(text, str):
        return text
    prev = None
    cur = text
    for _ in range(5):
        if cur == prev:
            break
        prev = cur
        cur = _combined_pattern.sub(lambda m: replacements[m.group(0)], cur)
    return cur


def encoding_repair(text):
    # Fix deep mojibake like 'KÃ?Â¤ptn' or 'l�¤cherlichen' into 'Käptn', 'lächerlichen'
    if not isinstance(text, str):
        return text

    for _ in range(5):
        try:
            new_text = text.encode("latin-1").decode("utf-8")
            # new_text = text.encode("utf-8").decode("utf-8")
            if new_text == text:
                break
            text = new_text
        except Exception:
            break

    # Decode HTML entities
    text = html.unescape(text)

    # Manual byte-sequence replacements
    replacements = {
        "�¤": "ä",
        "�¶": "ö",
        "�¼": "ü",
        "�Ÿ": "ß",
        "�„": "Ä",
        "�–": "Ö",
        "�œ": "Ü",
        "�?©": "é",
        "Ã¤": "ä",
        "Ã¶": "ö",
        "Ã¼": "ü",
        "ÃŸ": "ß",
        "Ã„": "Ä",
        "Ã–": "Ö",
        "Ãœ": "Ü",
        "Ã©": "é",
        "Ã¨": "è",
        "Ã¡": "á",
        "Ã³": "ó",
        "Ãí": "í",
        "Ãº": "ú",
        "Ã±": "ñ",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Normalize whitespace and artifacts
    text = re.sub(r"\s+", " ", text).strip()

    return text


def fix_mojibake(input_path, output_path, delimiter=';', problematic_encoding='latin-1'):

    cleaned_rows = []

    with open(input_path, mode='r', encoding=problematic_encoding, newline='') as infile:
        reader = csv.reader(infile, delimiter=delimiter)
        for i, row in enumerate(reader):

            cleaned_row = []
            for field in row:
                before = field
                after = encoding_repair(before)
                after = apply_manual_replacements(after)

                cleaned_row.append(after)
            cleaned_rows.append(cleaned_row)

    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=delimiter,
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerows(cleaned_rows)


fix_mojibake('BX-Books-clean.csv', 'BX-Books-Cleaned-v2.csv',
             delimiter=';', problematic_encoding='latin-1')
