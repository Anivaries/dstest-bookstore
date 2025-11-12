from django import forms

FIELD_CHOICES = [
    ('isbn', 'ISBN'),
    ('book_title', 'Book Title'),
    ('authors', 'Author'),
    ('publisher', 'Publisher'),
    ('year_of_publication', 'Year'),
    ('avg_rating', 'Rating'),
    ('total_ratings', 'Total Ratings'),
]

FORMAT_CHOICES = [
    ('csv', 'CSV'),
    ('tsv', 'TSV'),
    ('json', 'JSON'),
]


class DataExportForm(forms.Form):
    fields = forms.MultipleChoiceField(
        choices=FIELD_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Select fields to include'
    )
    file_format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        required=True,
        label='Select file format'
    )
