from django.contrib import admin
from .models import Author, Genre, Book
from django.db.models import Count

# Register your models here.


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "source_id", "review_count")
    search_fields = ("title", "authors__name")
    list_filter = ("genres",)
    ordering = ("title",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(num_reviews=Count("reviews"))

    @admin.display(ordering="num_reviews", description="Reviews")
    def review_count(self, obj):
        return obj.num_reviews


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    ordering = ("name",)