from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ProfileForm
from social.services import shelves_for
from .models import Profile
from social.services import reviews_by_user, shelves_for
from social.services import (
    followers_of, following_ids, following_of, reviews_by_user, shelves_for,
)
from django.core.paginator import Paginator
# Create your views here.

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


def profile_detail(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    owner = profile.user
    return render(
        request,
        "accounts/profile.html",
        {
            "owner": owner,
            "profile": profile,
            "shelves": shelves_for(profile.user),
            "reviews": reviews_by_user(profile.user),
            "following_ids": following_ids(request.user),
            "followers_count": followers_of(owner).count(),
            "following_count": following_of(owner).count(),
        },
    )

@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile_detail", username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, "accounts/profile_edit.html", {"form": form})




