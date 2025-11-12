import pandas as pd
import re


def is_valid_isbn10(isbn):
    """Validate an ISBN-10 number."""
    if not re.match(r'^\d{9}[\dXx]$', isbn):
        return False
    total = sum((i + 1) * (10 if x in 'Xx' else int(x))
                for i, x in enumerate(isbn))
    return total % 11 == 0


def is_valid_isbn13(isbn):
    """Validate an ISBN-13 number."""
    if not re.match(r'^\d{13}$', isbn):
        return False
    total = sum((int(x) * (1 if i % 2 == 0 else 3))
                for i, x in enumerate(isbn))
    return total % 10 == 0


def validate_isbn(isbn):
    """Check if ISBN is valid (10 or 13)."""
    if not isinstance(isbn, str):
        return False
    isbn = isbn.strip().replace("-", "").replace(" ", "")
    if len(isbn) == 10:
        return is_valid_isbn10(isbn)
    elif len(isbn) == 13:
        return is_valid_isbn13(isbn)
    else:
        pass
    return False


df = pd.read_csv(r"BX-Book-Ratings_new.csv", sep=";")


df['valid_isbn'] = df['ISBN'].apply(validate_isbn)


invalid_isbns = df[~df['valid_isbn']]
invalid_isbns.to_csv("invalid_isbns-books.csv", index=False)
