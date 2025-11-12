from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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
    authors = models.ManyToManyField(AuthorModel, related_name='books')
    year_of_publication = models.PositiveSmallIntegerField(
        null=True, blank=True)
    publisher = models.ForeignKey(
        PublisherModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='publisher_books')
    img_s = models.URLField(max_length=512, null=True, blank=True)
    img_m = models.URLField(max_length=512, null=True, blank=True)
    img_l = models.URLField(max_length=512, null=True, blank=True)

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
