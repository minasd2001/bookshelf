from django.contrib import admin
from .models import ShelfEntry, Review, Follow

admin.site.register(ShelfEntry)
admin.site.register(Review)
admin.site.register(Follow)