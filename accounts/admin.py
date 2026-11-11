from django.contrib import admin
from .models import Profile
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username",)
    raw_id_fields = ("user",)

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("date_joined", "review_count")
    ordering = ("-date_joined",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(num_reviews=Count("reviews"))

    @admin.display(ordering="num_reviews", description="Reviews")
    def review_count(self, obj):
        return obj.num_reviews    