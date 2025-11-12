import re
import unidecode

from django.core.management.base import BaseCommand
from django.db import connection

from bookstore.models import BookStoreModel


def normalize_author(name: str) -> str:
    if not name:
        return ""
    name = unidecode.unidecode(name).lower().strip()
    name = re.sub(r'[^a-z\s]', '', name)
    parts = [p.strip() for p in name.split(',')]
    if len(parts) == 2:
        name = f"{parts[1]} {parts[0]}"
    return re.sub(r'\s+', ' ', name)


def normalize_title(title: str) -> str:
    if not title:
        return ""

    title = title.lower().strip()

    title = unidecode.unidecode(title)

    title = re.sub(r'\([^)]*\)', '', title)
    title = re.sub(r'\[[^]]*\]', '', title)
    title = re.sub(
        r'\b(edition|ed\.?|vol\.?|volume|book|series|journal|guide|part|#?\d+)\b', '', title)
    title = re.sub(r'[^a-z0-9\s]', '', title)
    title = re.sub(r'\s+', ' ', title)

    return title.strip()


class Command(BaseCommand):
    BATCH_SIZE = 1000

    def handle(self, *args, **options):
        qs = BookStoreModel.objects.prefetch_related('authors')
        total = qs.count()
        self.stdout.write(f"Total books: {total}")

        books_to_update = []
        for book in qs.iterator(chunk_size=self.BATCH_SIZE):
            book.normalized_title = normalize_title(book.book_title)

            authors = [a.name for a in book.authors.all() if a.name]
            normalized_authors = " ".join(
                sorted([normalize_author(a) for a in authors if normalize_author(a)]))
            book.normalized_authors = normalized_authors

            books_to_update.append(book)

            if len(books_to_update) >= self.BATCH_SIZE:
                BookStoreModel.objects.bulk_update(
                    books_to_update, ['normalized_title', 'normalized_authors'])
                books_to_update = []

        if books_to_update:
            BookStoreModel.objects.bulk_update(
                books_to_update, ['normalized_title', 'normalized_authors'])
