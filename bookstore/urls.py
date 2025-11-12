from django.urls import path

from bookstore.views import IndexView, BookSearchView, AllBooksListView, BookDetailView, export_data
urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('books/', AllBooksListView.as_view(), name="books-list"),
    path('book/<str:isbn>/', BookDetailView.as_view(), name="book-detail"),
    path('export/', export_data, name="export_data"),
    path('search/', BookSearchView.as_view(), name="search_view"),
]
