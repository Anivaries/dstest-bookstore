import csv


def is_valid_isbn(isbn):
    """Check if the ISBN is valid (10 or 13 digits, last digit can be X for ISBN-10)."""
    isbn_clean = isbn.replace("-", "").replace(" ", "")
    if len(isbn_clean) == 10:
        return isbn_clean[:-1].isdigit() and (isbn_clean[-1].isdigit() or isbn_clean[-1].upper() == "X")
    elif len(isbn_clean) == 13:
        return isbn_clean.isdigit()
    return False


def is_integer(value):
    """Check if the value can be interpreted as an integer."""
    try:
        int(value)
        return True
    except ValueError:
        return False


input_file = "dstest/BX-Book-Ratings.csv"
output_file = "valid_isbns.csv"
log_file = "invalid_isbns.log"

with open(input_file, newline="", encoding="utf-8") as infile, \
        open(output_file, "w", newline="", encoding="utf-8") as outfile, \
        open(log_file, "w", encoding="utf-8") as log:

    reader = csv.DictReader(infile, delimiter=";")
    writer = csv.DictWriter(outfile, fieldnames=[
                            "User-ID", "ISBN", "Book-Rating"], delimiter=";")
    writer.writeheader()

    invalid_count = 0
    for i, row in enumerate(reader, start=1):
        isbn = row["ISBN"].strip().replace('"', '')
        user_id = row["User-ID"].strip().replace('"', '')
        rating = row["Book-Rating"].strip().replace('"', '')

        if is_valid_isbn(isbn):
            writer.writerow(
                {"User-ID": user_id, "ISBN": isbn, "Book-Rating": rating})
        else:
            invalid_count += 1
            log.write(
                f"Line {i}: Invalid ISBN '{isbn}' for User-ID {user_id}, Book-Rating {rating}\n")


print(f"✅ Valid ISBNs saved to {output_file}")
print(f"📝 {invalid_count} invalid ISBNs logged to {log_file}")
