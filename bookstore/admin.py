from django.contrib import admin

from . import models


class BookStoreAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'book_title', 'year_of_publication',
                    'publisher_name_display')
    list_filter = ('year_of_publication', 'publisher')
    search_fields = ('isbn', 'book_title')
    autocomplete_fields = ['authors', 'publisher']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('publisher').prefetch_related('authors')

    @admin.display(description='Publisher')
    def publisher_name_display(self, obj):
        return obj.publisher.name if obj.publisher else 'N/A'


admin.site.register(models.BookStoreModel, BookStoreAdmin)


class BookRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'rating', 'explicit_rating_display')
    list_filter = ('rating',)
    search_fields = ('user__user_id', 'book__book_title', 'book__isbn')
    list_select_related = ('user', 'book')
    raw_id_fields = ('user', 'book')

    @admin.display(description='Type', boolean=True)
    def explicit_rating_display(self, obj):
        return obj.rating is not None


admin.site.register(models.BookRatingModel, BookRatingAdmin)


@admin.register(models.AuthorModel)
class AuthorModelAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(models.PublisherModel)
class PublisherModelAdmin(admin.ModelAdmin):
    search_fields = ['name']


class BookReaderAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'ratings_count')
    search_fields = ('user_id',)

    @admin.display(description='Ratings Count')
    def ratings_count(self, obj):
        return obj.book_ratings.count()

    inlines = [
        type('BookRatingInline', (admin.TabularInline,), {
             'model': models.BookRatingModel, 'extra': 0})
    ]


admin.site.register(models.BookReaderModel, BookReaderAdmin)
