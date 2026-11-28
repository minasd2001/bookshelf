import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from books.importing import build_genre_lookup, import_book

# Tag names (from tags.csv) that we accept as genres.
# Check this against your top_tags.csv: delete what isn't a genre,
# add real genres I missed, and decide how to handle duplicates
# such as "sci-fi" vs "science-fiction".
GENRES = [
    "fantasy", "fiction", "young-adult", "romance", "mystery",
    "historical-fiction", "classics", "non-fiction", "science-fiction",
    "sci-fi", "horror", "thriller", "paranormal", "contemporary", "biography",
    "history", "memoir", "humor", "poetry",
    "graphic-novels", "comics", "crime", "dystopian", "adventure",
    "childrens", "religion", "philosophy", "self-help", "business",
    "urban-fantasy", "psychology", "science", "travel",
]


class Command(BaseCommand):
    help = "Import books, authors and genres from the Goodbooks-10k CSV files"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=None)

    def handle(self, *args, **options):
        books = pd.read_csv("data/books.csv")
        if options["limit"]:
            books = books.head(options["limit"])
        lookup = build_genre_lookup(
            pd.read_csv("data/book_tags.csv"), pd.read_csv("data/tags.csv"), GENRES
        )

        created = 0
        with transaction.atomic():
            for i, row in enumerate(books.itertuples(), start=1):
                if import_book(row, lookup):
                    created += 1
                if i % 1000 == 0:
                    self.stdout.write(f"Processed {i} books...")

        self.stdout.write(self.style.SUCCESS(f"Done. {created} new books created."))