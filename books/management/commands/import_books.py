import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from books.models import Author, Book, Genre

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
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Only import the first N books (for testing)",
        )

    def handle(self, *args, **options):
        books = pd.read_csv("data/books.csv")
        book_tags = pd.read_csv("data/book_tags.csv")
        tags = pd.read_csv("data/tags.csv")

        if options["limit"]:
            books = books.head(options["limit"])

        # Build a lookup: book_id -> its top 3 genre tags, most popular first
        tagged = book_tags.merge(tags, on="tag_id")
        tagged = tagged[tagged["tag_name"].isin(GENRES)]
        tagged = tagged.sort_values("count", ascending=False)
        top3 = tagged.groupby("goodreads_book_id").head(3)
        lookup = (
            top3.groupby("goodreads_book_id")["tag_name"].apply(list).to_dict()
        )

        created_count = 0

        with transaction.atomic():
            for i, row in enumerate(books.itertuples(), start=1):
                # Placeholder covers are stored as an empty string
                cover = row.image_url if isinstance(row.image_url, str) else ""
                if "nophoto" in cover:
                    cover = ""

                book, created = Book.objects.get_or_create(
                    source_id=int(row.book_id),
                    defaults={
                        "title": str(row.title)[:300],
                        "cover_url": cover[:500],
                    },
                )
                if created:
                    created_count += 1

                # Authors: split "A, B, C" into separate names
                for name in str(row.authors).split(","):
                    name = name.strip()
                    if not name:
                        continue
                    author, _ = Author.objects.get_or_create(name=name[:200])
                    book.authors.add(author)

                # Genres: up to 3 from the lookup
                for tag in lookup.get(int(row.book_id), []):
                    display_name = tag.replace("-", " ").title()
                    genre, _ = Genre.objects.get_or_create(name=display_name)
                    book.genres.add(genre)

                if i % 1000 == 0:
                    self.stdout.write(f"Processed {i} books...")

        self.stdout.write(
            self.style.SUCCESS(f"Done. {created_count} new books created.")
        )

