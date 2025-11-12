import csv
import io

from django.core.management.base import BaseCommand
from django.db import transaction
from bookstore.models import BookRatingModel, BookReaderModel, BookStoreModel, PublisherModel, AuthorModel


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--books_file', type=str,
                            help='The path to the books CSV file.', required=True)
        parser.add_argument('--ratings_file', type=str,
                            help='The path to the ratings CSV file.', required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        books_file_path = options['books_file']
        ratings_file_path = options['ratings_file']

        known_publishers = {}
        known_authors = {}
        authors_relationships_to_create = []

        try:
            with open(books_file_path, mode='r', encoding='utf-8', newline='') as file:
                # cleaned_lines = (line.replace(r'\"', '"').replace(
                #     r'"";', '";') for line in file)
                # cleaned_file_buffer = io.StringIO("".join(cleaned_lines))

                reader = csv.reader(file, delimiter=';',
                                    quoting=csv.QUOTE_MINIMAL)

                header = next(reader)
                for i, row in enumerate(reader):
                    try:
                        isbn = row[0]
                        title = row[1]
                        author_str = row[2]
                        year_str = row[3]
                        publisher_name = row[4]
                        img_s = row[5]
                        img_m = row[6]
                        img_l = row[7]

                        if publisher_name not in known_publishers:
                            publisher, _ = PublisherModel.objects.get_or_create(
                                name=publisher_name)
                            known_publishers[publisher_name] = publisher
                        else:
                            publisher = known_publishers[publisher_name]

                        try:
                            year = int(year_str)
                        except (ValueError, TypeError):
                            year = 0

                        book, created = BookStoreModel.objects.update_or_create(
                            isbn=isbn,
                            defaults={
                                'book_title': title,
                                'year_of_publication': year,
                                'publisher': publisher,
                                'img_s': img_s,
                                'img_m': img_m,
                                'img_l': img_l
                            }
                        )
                        author_names = [a.strip()
                                        for a in author_str.split(',')]
                        for author_name in author_names:
                            if author_name not in known_authors:
                                author, _ = AuthorModel.objects.get_or_create(
                                    name=author_name)
                                known_authors[author_name] = author
                            else:
                                author = known_authors[author_name]
                            authors_relationships_to_create.append(
                                (book.pk, author.pk))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(
                            f"Error processing book riw {i+2}: {row} > {e}"))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(
                f"File not found: {books_file_path}"))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
            return
        self.stdout.write(self.style.SUCCESS("Finished loading books."))

        if authors_relationships_to_create:
            self.stdout.write(
                f"Creating {len(authors_relationships_to_create)} author relationships.")
            BookAuthorThroughModel = BookStoreModel.authors.through
            relationship_objects = [
                BookAuthorThroughModel(
                    bookstoremodel_id=book_pk, authormodel_id=author_pk)
                # Use set to ensure unique pairs
                for book_pk, author_pk in set(authors_relationships_to_create)
            ]
            BookAuthorThroughModel.objects.bulk_create(
                relationship_objects,
                batch_size=1000,
                ignore_conflicts=True
            )
            self.stdout.write(self.style.SUCCESS(
                "All author relationships created."))

        existing_books = set(
            BookStoreModel.objects.values_list('isbn', flat=True))
        existing_readers = set(
            BookReaderModel.objects.values_list('user_id', flat=True))

        new_readers_to_create = []
        ratings_to_create = []

        new_readers_in_batch = set()

        try:
            with open(ratings_file_path, mode='r', encoding="utf-8", newline='') as file:
                reader = csv.reader(file, delimiter=';',
                                    quoting=csv.QUOTE_MINIMAL)
                header = next(reader)

                for i, row in enumerate(reader):
                    try:
                        user_id = row[0]
                        isbn = row[1]
                        rating_str = row[2]

                        if isbn not in existing_books:
                            continue
                        if user_id not in existing_readers and user_id not in new_readers_in_batch:
                            new_readers_to_create.append(
                                BookReaderModel(user_id=user_id))
                            new_readers_in_batch.add(user_id)

                        rating_val = int(rating_str)
                        rating_for_db = None if rating_val == 0 else rating_val

                        ratings_to_create.append(BookRatingModel(user_id=user_id,
                                                                 book_id=isbn,
                                                                 rating=rating_for_db))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(
                            f"Error processing rating row {i+2}: {row} > {e}"))
            if new_readers_to_create:
                self.stdout.write(
                    f"Creating {len(new_readers_to_create)} new readers")
                BookReaderModel.objects.bulk_create(
                    new_readers_to_create, ignore_conflicts=True)
                self.stdout.write(self.style.SUCCESS("New readers created."))
            if ratings_to_create:
                self.stdout.write(
                    f"Creating {len(ratings_to_create)} new ratings")
                BookRatingModel.objects.bulk_create(
                    ratings_to_create, batch_size=1000, ignore_conflicts=True)
                self.stdout.write(self.style.SUCCESS("New ratings created."))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(
                f"File not found: {ratings_file_path}"))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
            return
        self.stdout.write(self.style.SUCCESS("Data loading complete."))
