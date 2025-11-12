import csv
import requests
from django.core.management.base import BaseCommand
from bookstore.models import BookStoreModel  # adjust to your model
import time


def clean_title(title: str) -> str:
    if not title:
        return title

    title = title.replace('\"', '"')

    if title.startswith('"') and title.endswith('"'):
        title = title[1:-1]

    return title


class Command(BaseCommand):
    help = 'Clean book titles with quotes using OpenLibrary in batches'

    BATCH_SIZE = 25  # number of ISBNs per API call

    def handle(self, *args, **options):
        # 1️⃣ Find books with quotes in the title
        books_with_quotes = BookStoreModel.objects.filter(
            book_title__contains='"')

        # 2️⃣ Process in batches
        books_list = list(books_with_quotes)
        total = len(books_list)
        self.stdout.write(f"Found {total} books with quotes in title.")
        time.sleep(1)
        with open('cleaned_titles_preview.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(
                csvfile, quoting=csv.QUOTE_NONE, escapechar='\\')
            writer.writerow(['ISBN', 'Old Title', 'New Title'])

            for i in range(0, total, self.BATCH_SIZE):

                batch = books_list[i:i + self.BATCH_SIZE]
                isbns = [book.isbn for book in batch if book.isbn]
                if not isbns:
                    continue

                # Build API URL with multiple ISBNs
                isbn_str = ','.join(f"ISBN:{isbn}" for isbn in isbns)
                url = f"https://openlibrary.org/api/books?bibkeys={isbn_str}&format=json&jscmd=data"

                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json()

                    for book in batch:
                        key = f"ISBN:{book.isbn}"
                        if key in data:
                            ol_title = data[key].get("title")
                            if ol_title:
                                cleaned_title = clean_title(ol_title)
                                old_title = book.book_title
                                book.book_title = cleaned_title.replace(
                                    '\\"', '"')
                                book.save()
                                writer.writerow(
                                    [book.isbn, book.book_title, cleaned_title])
                                # self.stdout.write(
                                # f'Updated "{old_title}" → "{cleaned_title}"')
                            else:
                                self.stdout.write(
                                    f"No title found for ISBN {book.isbn}")
                        else:
                            self.stdout.write(
                                f"No data found for ISBN {book.isbn}")

                except requests.RequestException as e:
                    self.stdout.write(
                        f"Error fetching batch starting at index {i}: {e}")
