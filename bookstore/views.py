import csv
import os
import json
import pandas as pd
import random
from collections import defaultdict

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from django.db.models import Avg, Count, Q


from bookstore.models import BookStoreModel, BookRatingModel, BookReaderModel, BookExportView
from bookstore.forms import DataExportForm

from django.conf import settings
from django.db.models import CharField
from django.db.models.functions import Lower
from django.http import FileResponse, Http404


CharField.register_lookup(Lower)

MIN_RATINGS = 8
CANDIDATE_MIN_RATINGS = 8
TOP_N = 12

DOWNLOAD_DIR = os.path.join(settings.BASE_DIR, 'bookstore/downloads')


def make_book_key(book):
    return f"{book.normalized_title} {book.normalized_authors}".strip()


def recommend_books(isbn,):
    book = BookStoreModel.objects.get(isbn=isbn)
    target_books = BookStoreModel.objects.filter(
        normalized_title=book.normalized_title)
    total_ratings = BookRatingModel.objects.filter(
        book__in=target_books,
        rating__isnull=False
    ).count()
    if total_ratings < MIN_RATINGS:

        # Fallback: same author
        authors = book.authors.all()
        fallback_books = BookStoreModel.objects.filter(authors__in=authors).exclude(
            isbn=book.isbn).annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')[:TOP_N]

        if fallback_books:
            return [{'fb_author': True, 'book': {'title': b.book_title, 'isbn': b.isbn, 'author': b.authors.get(), 'avg_rating': b.avg_rating, 'img': b.img_m}} for b in fallback_books]
        # Fallback if author doesn't have enough books. Randoms top 10 rated books with 9 or 10 rating. Can be improved with at least

        eligible_books_qs = BookStoreModel.objects.annotate(
            avg_rating=Avg('ratings__rating', filter=Q(
                ratings__rating__isnull=False)),
            num_ratings=Count('ratings')).exclude(isbn=book.isbn).filter(avg_rating__gte=9, num_ratings__gte=8)

        book_ids = list(eligible_books_qs.values_list('isbn', flat=True))
        random_ids = random.sample(book_ids, k=min(10, len(book_ids)))

        random_top_books = BookStoreModel.objects.annotate(
            avg_rating=Avg('ratings__rating')).filter(isbn__in=random_ids)

        return [{'fb_top_rated': True, 'book': {'title': b.book_title, 'isbn': b.isbn, 'author': b.authors.get(), 'avg_rating': b.avg_rating, 'img': b.img_m}} for b in random_top_books]
    # Collaborative filtering
    readers = BookReaderModel.objects.filter(
        book_ratings__book__in=target_books,
        book_ratings__rating__isnull=False
    ).distinct()

    ratings_qs = BookRatingModel.objects.filter(
        user__in=readers,
        rating__isnull=False
    ).select_related('book').prefetch_related('book__authors')

    ratings_dict = defaultdict(list)
    for r in ratings_qs:
        key = f"{r.book.normalized_title} {r.book.normalized_authors}"
        ratings_dict[key].append((r.user_id, r.rating))

    selected_key = f"{book.normalized_title} {book.normalized_authors}"

    books_to_compare_keys = [
        key for key, vals in ratings_dict.items() if len(vals) >= MIN_RATINGS]

    rows = []
    for key in books_to_compare_keys:
        for user_id, rating in ratings_dict[key]:
            rows.append(
                {'user_id': user_id, 'book_key': key, 'rating': rating})

    df = pd.DataFrame(rows)
    df = df.groupby(['user_id', 'book_key'], as_index=False)['rating'].mean()
    pivot_df = df.pivot(index='user_id', columns='book_key', values='rating')
    pivot_df = pivot_df[pivot_df[selected_key].notna()]

    correlations = pivot_df.corrwith(pivot_df[selected_key]).drop(
        selected_key).sort_values(ascending=False)

    recommendations = []
    # print("Books to compare:", books_to_compare_titles)
    # for title in books_to_compare_titles:
    #     print(title, len(ratings_dict[title])) # An issue here is that 'fellowship of the ring' is not matching longer versions of the title ( LIke LOTR Fellowship of the.. ). The pivot includes all other users who rated any edition. So those users are not matched with the book and it returns all NaNs. Fix here is to normalize book titles
    if correlations.empty:
        # Too little ratings to have enough users for corrwith, 'fixing' this would be using smaller number for CANDIDATE_MIN_RATINGS
        return recommendations
    # Fetch top_n books from correlations
    top_keys = correlations.head(TOP_N).index.tolist()

    seen_isbns = set()
    for key in top_keys:

        # Find editions with same normalized title and author
        candidates = (
            BookStoreModel.objects
            .filter(
                # crude start; can improve
                normalized_title__icontains=key.split()[0],
                normalized_authors__icontains=" ".join(
                    key.split()[len(key.split())-2:])
            )
            .annotate(avg_rating=Avg('ratings__rating'))
            .filter(avg_rating__isnull=False)
            .order_by('-avg_rating')
        )

        b = candidates.first()
        if not b or b.isbn in seen_isbns:
            continue

        seen_isbns.add(b.normalized_title)

        recommendations.append({
            'algo': True,
            'book': {
                'title': b.book_title,
                'avg_rating': b.avg_rating,
                'isbn': b.isbn,
                'author': b.authors.first(),
                'corr': correlations[key],
                'img': b.img_m
            }
        })

    return recommendations


class IndexView(TemplateView):
    template_name = 'index.html'


class AllBooksListView(ListView):
    model = BookStoreModel
    paginate_by = 16
    context_object_name = 'books'
    template_name = 'books_list.html'
    ordering = ['isbn']

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class BookDetailView(DetailView):
    model = BookStoreModel
    context_object_name = 'book'
    template_name = 'book_detail.html'
    pk_url_kwarg = 'isbn'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object
        total_ratings = book.ratings.exclude(rating__isnull=True).count()
        avg_rating = book.ratings.aggregate(Avg('rating'))['rating__avg']
        context['total_ratings'] = total_ratings
        recomm_books = recommend_books(book.isbn)

        if recomm_books:
            items_per_slide = 3
            slides = [recomm_books[i:i + items_per_slide]
                      for i in range(0, len(recomm_books), items_per_slide)]
            indicators = range(len(slides))
            context['slides'] = slides
            context['recomm_books'] = recomm_books
            context['indicators'] = indicators
        else:
            context['low_corr'] = True
        if avg_rating != None:
            context['avg_rating'] = round(avg_rating, 1)
        else:
            context['avg_rating'] = None
        return context


class BookSearchView(ListView):
    model = BookStoreModel
    template_name = 'books_list.html'
    context_object_name = 'books'
    paginate_by = 16

    def get_queryset(self):
        query = self.request.GET.get('search', '').lower().strip()
        qs = BookStoreModel.objects.all().order_by('book_title')
        if query:
            qs = qs.filter(book_title__icontains=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        querydict = self.request.GET.copy()
        querydict.pop('page', None)
        context['querystring'] = querydict.urlencode()
        return context


def export_data(request):
    form = DataExportForm(request.GET or None)
    filename = request.GET.get('download')
    if filename:
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        if not os.path.exists(filepath):
            raise Http404("File not found")

        return FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
    if form.is_valid():
        selected_fields = form.cleaned_data['fields']
        file_format = form.cleaned_data['file_format']

        qs = BookExportView.objects.all().values(*selected_fields)

        if file_format == 'json':
            response = HttpResponse(json.dumps(
                list(qs), indent=4, ensure_ascii=False), content_type='application/json; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="books.json"'
            return response
        elif file_format in ['csv', 'tsv']:
            delimiter = ';' if file_format == 'csv' else '\t'
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="books.{file_format}"'

            writer = csv.DictWriter(response, fieldnames=list(
                qs[0].keys()), delimiter=delimiter)
            writer.writeheader()
            writer.writerows(list(qs))
            return response
    existing_files = []
    if os.path.exists(DOWNLOAD_DIR):
        existing_files = [
            f for f in os.listdir(DOWNLOAD_DIR)
            if f.endswith(('.csv', '.json', '.tsv'))
        ]

    context = {
        'form': form,
        'existing_files': existing_files
    }

    return render(request, 'export.html', context)

# TODO

# Check what to do with those amazon B000 books
# A bunch of books with no publications date, can be fixed

# http://127.0.0.1:8000/book/0618260250/ - not enough data for .corrwith()
# http://127.0.0.1:8000/book/0345339681/ enough for personalized recommendation

# https://isbnsearch.org/isbn/2207301656

# Multiple authors: 0721646522, 3453212614


# TODO:
# Check book names, some of them are not utf on export/ TEST THIS
# Fix 'Not Avail' in publisher col, books.csv
# Upload code to git
# Run the code on server
# Create presentation

# Things to improve:
# An "issue" with The Divine Secrets of the Ya-Ya Sisterhood. Where one book has 'the' in the tittle so pandas doesn't recognize it. In django __icontains work fine


# Users’ ratings for multiple editions are averaged into one per title
# Correlations are title-level, not edition-level
# What i couldve done differently:If we could include different editions then we could change primary key to normalized book title and then list all editions of that book which would be their title from the csv file. The book would have aggregated rating from all editions, but then each edition would have it's own page with it's own ratings
#

# Script doesn't address books which have some extra edition like "Journal", "Guide", "Photo guide", "Visual Companion" so "Fellowship of the ring" won't work when searched but "The Fellowship of the Ring (The Lord of the Rings, Part 1)" will
# Problems: How should books be listed? By isbn or by title.
# By isbn:
#   Each book can be seen as an entity since it has an identifyer in ISBN
# Issue:
#   Each edition has it's own rating, so ratings can't be properly calculated for the title. Finding total ratings for the title can be tricky because each book has different editions ( hard cover, soft cover, typo fixes, title changes like "The Divine Secrets of the Ya-Ya Sisterhood").
# Solution:

# By title:
#   Each title can be a book identifyer. Normalazing title for different books and grouping it under one entity while keeping track of different editions. This means having one title as identifyer "Fellowship of the ring" and grouping all ratings from all different editions under it's title.
