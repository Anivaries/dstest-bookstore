import csv
import json
from django.core.management.base import BaseCommand
from bookstore.models import BookRatingModel


class Command(BaseCommand):
    help = "Export BookRatingModel data to JSON, CSV, or TSV"

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv', 'tsv', 'json'],
            default='csv',
            help='Export format (csv, tsv, json)',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='book_ratings_export',
            help='Output filename (without extension)',
        )

    def handle(self, *args, **options):
        export_format = options['format']
        filename = f"{options['output']}.{export_format}"

        ratings = BookRatingModel.objects.select_related('user', 'book').all()

        if export_format == 'json':
            self.export_json(ratings, filename)
        else:
            delimiter = ',' if export_format == 'csv' else '\t'
            self.export_csv_tsv(ratings, filename, delimiter)

        self.stdout.write(self.style.SUCCESS(
            f"✅ Exported {ratings.count()} ratings to {filename}"))

    def export_json(self, ratings, filename):
        data = {}

        for rating in ratings:
            isbn = rating.book.isbn
            if isbn not in data:
                data[isbn] = {
                    "ratings": []
                }

            data[isbn]["ratings"].append({
                "user_id": rating.user.user_id,
                "rating": rating.rating if rating.rating is not None else 0,
            })

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def export_csv_tsv(self, ratings, filename, delimiter):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=delimiter,
                                quoting=csv.QUOTE_MINIMAL)

            writer.writerow(['User ID', 'ISBN', 'Rating'])

            for r in ratings:
                writer.writerow([
                    r.user.user_id,
                    r.book.isbn,
                    r.rating if r.rating is not None else 0,
                ])
