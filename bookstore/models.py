import re
import unidecode

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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


class AuthorModel(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class PublisherModel(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class BookReaderModel(models.Model):
    user_id = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return f"User {self.user_id}"


class BookStoreModel(models.Model):
    isbn = models.CharField(max_length=13, primary_key=True)
    book_title = models.CharField(max_length=512)
    normalized_title = models.CharField(max_length=255, editable=False)
    authors = models.ManyToManyField(AuthorModel, related_name='books')
    normalized_authors = models.CharField(max_length=255, editable=False)
    year_of_publication = models.PositiveSmallIntegerField(
        null=True, blank=True)
    publisher = models.ForeignKey(
        PublisherModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='publisher_books')
    img_s = models.URLField(max_length=512, null=True, blank=True)
    img_m = models.URLField(max_length=512, null=True, blank=True)
    img_l = models.URLField(max_length=512, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.normalized_title = normalize_title(self.book_title)
        self.normalized_authors = " ".join(
            sorted([normalize_author(a.name) for a in self.authors.all()]))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book_title}"


class BookRatingModel(models.Model):
    user = models.ForeignKey(
        BookReaderModel,
        on_delete=models.CASCADE,
        related_name='book_ratings'
    )
    book = models.ForeignKey(
        BookStoreModel, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(10)
    ], null=True, blank=True)

    class Meta:
        unique_together = ('user', 'book')


class BookExportView(models.Model):
    isbn = models.CharField(max_length=13, primary_key=True)
    book_title = models.CharField(max_length=512)
    authors = models.TextField()
    publisher = models.CharField(max_length=255, null=True, blank=True)
    year_of_publication = models.PositiveSmallIntegerField(
        null=True, blank=True)
    avg_rating = models.FloatField(null=True, blank=True)
    total_ratings = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'book_export_view'
