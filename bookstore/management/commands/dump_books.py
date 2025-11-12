import csv
import json
from django.core.management.base import BaseCommand
from bookstore.models import BookStoreModel


class Command(BaseCommand):
    help = "Export BookStoreModel data to CSV, TSV, or JSON"

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv', 'tsv', 'json'],
            default='csv',
            help='File format to export (csv, tsv, json)',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='books_export',
            help='Output filename (without extension)',
        )

    def handle(self, *args, **options):
        export_format = options['format']
        filename = f"{options['output']}.{export_format}"

        books = BookStoreModel.objects.all().prefetch_related('authors', 'publisher')

        if export_format in ['csv', 'tsv']:
            delimiter = ',' if export_format == 'csv' else '\t'
            self.export_csv_tsv(books, filename, delimiter)
        elif export_format == 'json':
            self.export_json(books, filename)

        self.stdout.write(self.style.SUCCESS(
            f"✅ Exported {books.count()} books to {filename}"))

    def export_csv_tsv(self, books, filename, delimiter):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=delimiter,
                                quoting=csv.QUOTE_MINIMAL)

            # Write header
            writer.writerow([
                'ISBN', 'Book Title', 'Authors', 'Publisher',
                'Year of Publication', 'Img_S', 'Img_M', 'Img_L'
            ])

            # Write rows
            for book in books:
                authors = ', '.join(a.name for a in book.authors.all())
                publisher = book.publisher.name if book.publisher else ''
                writer.writerow([
                    book.isbn,
                    book.book_title,
                    authors,
                    publisher,
                    book.year_of_publication or '',
                    book.img_s or '',
                    book.img_m or '',
                    book.img_l or '',
                ])

    def export_json(self, books, filename):
        data = {}
        for book in books:
            data[book.isbn] = {
                'book_title': book.book_title,
                'authors': [a.name for a in book.authors.all()],
                'publisher': book.publisher.name if book.publisher else None,
                'year_of_publication': book.year_of_publication,
                'img_s': book.img_s,
                'img_m': book.img_m,
                'img_l': book.img_l,
            }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
