from books.models import Book,Genre
from social.models import ShelfEntry, Review
from dataclasses import dataclass
from django.db.models import Avg, Count, ExpressionWrapper, F, FloatField
from social import services

@dataclass
class Suggestion:
    book : Book
    score : float
    reason : str

class FreindsLikedStrategy:
    weight = 3.0

    def suggest(self, user, exclude_ids, limit):
        books = (
            Book.objects
                .filter(reviews__user__in=services.following_of(user), reviews__rating__gte=4)
                .exclude(pk__in=exclude_ids)
                .annotate(fans=Count("reviews__user", distinct=True))
                .order_by("-fans")[:limit]
                )

        top = max((b.fans for b in books), default=1) # if empty return 1 instead of crash
        return [
            Suggestion(b, b.fans/top ,f"Liked by {b.fans} people you follow" )
            for b in books
        ]

def seen_ids(user):
    shelved = ShelfEntry.objects.filter(user=user).exclude(status = ShelfEntry.Status.TO_READ).values_list("book_id", flat=True)
    return set(shelved)

class GenresLikedStrategy:
    weight = 5.0
    def suggest(self, user, exclude_ids, limit):

        top_genres = (
            Book.objects
            .filter(reviews__user=user, reviews__rating__gte=4, genres__isnull=False)
            .values("genres__name") #grouped by genre name
            .annotate(n=Count("pk", distinct=True)) #by frequency
            .order_by("-n")[:5]
        )
        names = [row["genres__name"] for row in top_genres]
        if not names:
            return []
        
        books = (Book.objects
                .filter(genres__name__in=names, reviews__rating__gte=3)
                .exclude(pk__in=exclude_ids)
                .annotate(fans=Count("reviews__user", distinct=True))
                .order_by("-fans")[:limit])

        top = max((b.fans for b in books), default=1)
        return [
            Suggestion(b, b.fans/top, "Books from your favourite genres")for b in books
        ]


MIN_RATINGS_TRUSTED = 10

class PopularStrategy:
    weight = 1.0
    def suggest(self, user, exclude_ids, limit):
        m = MIN_RATINGS_TRUSTED
        c = Review.objects.aggregate(c=Avg("rating"))["c"] or 3.5

        books = (
            Book.objects
                .exclude(pk__in=exclude_ids)
                .annotate(n=Count("reviews", distinct=True), avg=Avg("reviews__rating"))
                .filter(n__gt=0)
                .annotate(
                    weighted=ExpressionWrapper(
                        (F("n") * F("avg") + m * c) / (F("n") + m),
                        output_field=FloatField(),
                ))
                .order_by("-weighted", "title")[:limit]
                )

        top = max((b.weighted for b in books), default=1) # if empty return 1 instead of crash
        return [
            Suggestion(b, b.weighted ,f"Liked by other {b.n} readers" )
            for b in books
        ]
        

#return a dict that has all of them
# group by each one
class Recommender:
    def __init__(self, strategies):
        self.strategies = strategies

    def for_user(self, user, limit=12):
        exclude = seen_ids(user)
        combined = {}

        for strategy in self.strategies:
            for s in strategy.suggest(user, exclude, limit*3):
                entry = combined.setdefault( #checks if  key already exists in  dictionary
                s.book.pk, {"book": s.book, "score": 0, "reasons": []}
            )
                entry["score"] += strategy.weight * s.score
                entry["reasons"].append(s.reason)
    
        ranked = sorted(combined.values(), key=lambda e: e["score"], reverse=True)
        return ranked[:limit]   
                 

def default_recommender():
    return Recommender([FreindsLikedStrategy(), GenresLikedStrategy(),PopularStrategy()])