from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author) # amny to many doesnt accept cascade delete
    genres = models.ManyToManyField(Genre, blank=True)
    cover_url = models.URLField(max_length=500, blank=True)
    synopsis = models.TextField(blank=True)

    def __str__(self):
        return self.title
