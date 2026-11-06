from django.contrib.auth.models import User
from django.db import models

from books.models import Book


class ShelfEntry(models.Model):
    class Status(models.TextChoices):
        FINISHED = "finished", "Finshed"
        CURRENTLY_READING = "currently reading", "Currently Reading"
        DID_NOT_FINISH = "dnf", "Didn't finish"
        TO_READ = "to_read", "To read"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shelf_entries")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="shelf_entries")
    status = models.CharField(max_length=20, choices=Status.choices)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"], name="one_shelf_entry_per_user_book"
            ),
        ]

    # __str__ controls how an object is displayed as text
    def __str__(self):
        return f"{self.user.username}: {self.book.title} ({self.status})"

                                                                                                                                                                                                                                                                                                          
# movies/models.py
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    text = models.TextField(max_length=2000, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created"]
        constraints = [
            models.UniqueConstraint(fields=["user", "book"], name="one_review_per_user_book"),
        ]

    @property
    def stars(self):
        return "★" * self.rating + "☆" * (5 - self.rating)        

    def __str__(self):
        return f"{self.user.username}: {self.book.title} ({self.rating})"


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="i_follow")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="they_follow_me")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followed"], name="unique_follow"
            ),
            models.CheckConstraint( # don't follow yourself
                condition=~models.Q(follower=models.F("followed")), name="no_follow_yourself"),
        ]

    def __str__(self):
        return f"{self.follower.username} follows  {self.followed.username}"    