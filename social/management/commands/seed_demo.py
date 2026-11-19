import random

import pandas as pd
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Profile
from books.models import Book
from social.models import Follow, Review, ShelfEntry

COMMENTS = {
    5: ["Loved it!", "One of my all-time favourites.", "Couldn't put it down.",
        "Brilliant from start to finish."],
    4: ["Really enjoyed this one.", "A great read, would recommend.",
        "Very good, with a few slow parts."],
    3: ["It was okay.", "Decent, but not memorable.", "Some good ideas, uneven pacing."],
    2: ["Struggled to get into it.", "Not for me.", "Disappointing."],
    1: ["Could not finish it.", "Did not enjoy this at all.", "A real letdown."],
}


class Command(BaseCommand):
    help = "Create demo readers from the Goodbooks-10k ratings"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=3000)

    def handle(self, *args, **options):
        random.seed(1)
        ratings = pd.read_csv("data/ratings.csv")
        to_read = pd.read_csv("data/to_read.csv")

        catalog = pd.read_csv("data/books.csv", usecols=["id", "book_id"])
        id_to_source = dict(zip(catalog["id"], catalog["book_id"]))

        ratings["book_id"] = ratings["book_id"].map(id_to_source)
        to_read["book_id"] = to_read["book_id"].map(id_to_source)

        books = Book.objects.in_bulk(field_name="source_id")
        known = list(books)

        ratings = ratings[ratings["book_id"].isin(known)]
        counts = ratings.groupby("user_id").size().sort_values(ascending=False)
        chosen = list(counts.head(options["users"]).index)

        ratings = ratings[ratings["user_id"].isin(chosen)]
        to_read = to_read[
            to_read["user_id"].isin(chosen) & to_read["book_id"].isin(known)
        ]

        with transaction.atomic():
            # Hash the demo password once and reuse it for every user
            password = make_password("demo12345")
            User.objects.bulk_create(
                [User(username=f"reader_{uid}", password=password) for uid in chosen],
                ignore_conflicts=True,
            )
            by_name = {
                u.username: u for u in User.objects.filter(username__startswith="reader_")
            }
            users = {uid: by_name[f"reader_{uid}"] for uid in chosen}

            # bulk_create skips signals, so the profiles are created here
            Profile.objects.bulk_create(
                [Profile(user=u) for u in users.values()], ignore_conflicts=True
            )

            reviews = []
            for r in ratings.itertuples():
                rating = int(r.rating)
                text = random.choice(COMMENTS[rating]) if random.random() < 0.1 else ""
                reviews.append(Review(
                    user=users[r.user_id], book=books[int(r.book_id)],
                    rating=rating, text=text,
                ))
            Review.objects.bulk_create(reviews, ignore_conflicts=True)

            # "read" rows go in first, so a book in both files stays "read"
            ShelfEntry.objects.bulk_create(
                [
                    ShelfEntry(user=users[r.user_id], book=books[int(r.book_id)],
                               status=ShelfEntry.Status.FINISHED)
                    for r in ratings.itertuples()
                ],
                ignore_conflicts=True,
            )
            ShelfEntry.objects.bulk_create(
                [
                    ShelfEntry(user=users[r.user_id], book=books[int(r.book_id)],
                               status=ShelfEntry.Status.TO_READ)
                    for r in to_read.itertuples()
                ],
                ignore_conflicts=True,
            )

            people = list(users.values())
            follows = []
            for person in people:
                for other in random.sample(people, random.randint(6, 16)):
                    if other != person:
                        follows.append(Follow(follower=person, followed=other))
            Follow.objects.bulk_create(follows, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(
            f"Users: {User.objects.count()}, reviews: {Review.objects.count()}, "
            f"shelf entries: {ShelfEntry.objects.count()}, follows: {Follow.objects.count()}"
        ))