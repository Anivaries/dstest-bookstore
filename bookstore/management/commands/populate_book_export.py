from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Refresh the book_export_view materialized view"

    def handle(self, *args, **options):
        self.stdout.write("Refreshing book_export_view...")

        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW book_export_view;")

        self.stdout.write(self.style.SUCCESS(
            "✅ book_export_view successfully refreshed."
        ))
