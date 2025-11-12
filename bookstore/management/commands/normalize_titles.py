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
        qs = BookStoreModel.objects.prefetch_related('authors').all()
        total = qs.count()
        self.stdout.write(f"Total books: {total}")

        for start in range(0, total, self.BATCH_SIZE):
            end = min(start + self.BATCH_SIZE, total)
            books = qs[start:end]

            books_to_update = []

            for book in books:
                book.normalized_title = normalize_title(book.book_title)
                authors = [a.name for a in book.authors.all()]
                book.normalized_authors = " ".join(
                    sorted([normalize_author(a) for a in authors]))
                books_to_update.append(book)

            BookStoreModel.objects.bulk_update(
                books_to_update, ['normalized_title', 'normalized_authors'])
            self.stdout.write(self.style.SUCCESS(
                f"Updated books {start + 1}-{end}"))
