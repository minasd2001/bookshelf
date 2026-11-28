from .models import Author, Book, Genre


def clean_cover(url):
    """Return a usable cover URL, or '' for missing and placeholder covers."""
    if not isinstance(url, str) or "nophoto" in url:
        return ""
    return url[:500]


def split_authors(text):
    names = [name.strip() for name in str(text).split(",")]
    return [name[:200] for name in names if name]


def genre_display_name(tag):
    return tag.replace("-", " ").title()


def build_genre_lookup(book_tags, tags, allowed, per_book=3):
    """{goodreads_book_id: [its most popular allowed tags]}"""
    tagged = book_tags.merge(tags, on="tag_id")
    tagged = tagged[tagged["tag_name"].isin(allowed)]
    tagged = tagged.sort_values("count", ascending=False)
    top = tagged.groupby("goodreads_book_id").head(per_book)
    return top.groupby("goodreads_book_id")["tag_name"].apply(list).to_dict()


def import_book(row, genres_by_book):
    """Create one book with its authors and genres. Returns True if it was new."""
    cover = clean_cover(row.image_url)
    if not cover:
        return False

    book, created = Book.objects.get_or_create(
        source_id=int(row.book_id),
        defaults={"title": str(row.title)[:300], "cover_url": cover},
    )
    for name in split_authors(row.authors):
        author, _ = Author.objects.get_or_create(name=name)
        book.authors.add(author)
    for tag in genres_by_book.get(int(row.book_id), []):
        genre, _ = Genre.objects.get_or_create(name=genre_display_name(tag))
        book.genres.add(genre)
    return created