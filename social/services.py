from .models import ShelfEntry, Review


def set_shelf(user, book, status):
    """Put a book on a shelf, moving it if it's already on another one."""
    if status not in ShelfEntry.Status.values:
        raise ValueError("Invalid shelf status")
    entry, _ = ShelfEntry.objects.update_or_create(
        user=user, book=book, defaults={"status": status}
    )
    return entry


def remove_from_shelf(user, book):
    ShelfEntry.objects.filter(user=user, book=book).delete()


def shelf_status(user, book):
    """The status of this book for this user, or None."""
    if not user.is_authenticated:
        return None
    entry = ShelfEntry.objects.filter(user=user, book=book).first()
    return entry.status if entry else None


def shelves_for(user):
    """Return [(label, [books]), ...] in shelf order, for the profile page."""
    entries = (
        ShelfEntry.objects.filter(user=user)
        .select_related("book")
        .order_by("-updated")
    )
    grouped = {value: [] for value in ShelfEntry.Status.values}
    for entry in entries:
        grouped[entry.status].append(entry.book)
    return [(label, grouped[value]) for value, label in ShelfEntry.Status.choices]


def save_review(user, book, rating, text):
    review,_ = Review.objects.update_or_create(
        user=user, book=book, defaults={"rating": rating, "text": text}
    )
    return review

def delete_review(user, book):
    Review.objects.filter(user=user, book=book).delete()

def review_by(user, book):
    if not user.is_authenticated:
        return None
    return Review.objects.filter(user=user, book=book).first()

def reviews_for_book(book):
    return Review.objects.filter(book=book).select_related("user")

# select_related loads each review’s user (or book) in the same query
#  so 20 reviews don’t cause 20 extra queries

def reviews_by_user(user):
    return Review.objects.filter(user=user).select_related("book")