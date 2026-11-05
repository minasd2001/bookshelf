from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .forms import ReviewForm
from books.models import Book
from . import services


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
    form = ReviewForm(request.POST)
    if form.is_valid():
        services.save_review(
            request.user, book, form.cleaned_data["rating"], form.cleaned_data["text"]
        )
    return redirect("book_detail", pk=book.pk)

@login_required
@require_POST
def review_delete(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    services.delete_review(request.user, book)
    return redirect("book_detail", pk=book.pk)