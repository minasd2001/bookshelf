from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import ReviewForm
from books.models import Book
from . import services
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages

@login_required
@require_POST
def shelf_set(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    status = request.POST.get("status", "")
    if status == "remove":
        services.remove_from_shelf(request.user, book)
    else:
        try:
            services.set_shelf(request.user, book, status)
        except ValueError:
            pass  # a tampered value is ignored; the page simply reloads
    return redirect("book_detail", pk=book.pk)

@login_required
@require_POST
def review_save(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    form = ReviewForm(request.POST)  # wrap the submitted data in the form
    if form.is_valid():
        services.save_review(
            request.user, book, form.cleaned_data["rating"], form.cleaned_data["text"]
            #the form deliberately has no user or book field, so the browser has no way to say whose review it is
        )
        messages.success(request, "Your review was saved.")
    else:
        messages.error(request, "Please choose a star rating.")
    return redirect("book_detail", pk=book.pk)

@login_required
@require_POST
def review_delete(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    services.delete_review(request.user, book)
    return redirect("book_detail", pk=book.pk)

def _back_to(request, fallback):
    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return next_url
    return fallback


@login_required
@require_POST
def follow_user(request, username):
    target = get_object_or_404(User, username=username)
    try:
        services.follow(request.user, target)
    except ValueError:
        pass
    return redirect(_back_to(request, reverse("profile_detail", args=[username])))
   
@login_required
@require_POST
def unfollow_user(request, username):
    
    target = get_object_or_404(User, username=username)
    services.unfollow(request.user, target)
    return redirect(_back_to(request, reverse("profile_detail", args=[username])))

def followers_list(request, username):
    owner = get_object_or_404(User, username=username)
    return render(request, "social/follow_list.html", {
        "owner": owner,
        "title": "Followers",
        "people": services.followers_of(owner).select_related("profile"),
        "following_ids": services.following_ids(request.user),
    })


def following_list(request, username):
    owner = get_object_or_404(User, username=username)
    return render(request, "social/follow_list.html", {
        "owner": owner,
        "title": "Following",
        "people": services.following_of(owner).select_related("profile"),
        "following_ids": services.following_ids(request.user),
    })

