from django.contrib import admin
from .models import ShelfEntry, Review, Follow


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "rating", "created")
    list_filter = ("rating",)
    search_fields = ("user__username", "book__title")
    ordering = ("-created",)
    list_select_related = ("user", "book")
    raw_id_fields = ("user", "book")


@admin.register(ShelfEntry)
class ShelfEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "status", "updated")
    list_filter = ("status",)
    search_fields = ("user__username", "book__title")
    list_select_related = ("user", "book")
    raw_id_fields = ("user", "book")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "followed")
    search_fields = ("follower__username", "followed__username")
    list_select_related = ("follower", "followed")
    raw_id_fields = ("follower", "followed")