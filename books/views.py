from django.shortcuts import render, get_object_or_404
from .models import Book, Author
from django.core.paginator import Paginator
from django.db.models import Q, Avg # for multiple field search
from social import services as shelf_services
from social.models import ShelfEntry
from social import recommendations
from social import services as social_services
from social.forms import ReviewForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# Create your views here.

def home(request):
    books = Book.objects.order_by("source_id")[:12]
    recs = []
    if request.user.is_authenticated:
        recs = recommendations.default_recommender().for_user(request.user)
    return render(request, "books/home.html", {"books": books, "recs":recs})


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    my_review = social_services.review_by(request.user, book)
    context = {
        "book": book,
        "my_status": social_services.shelf_status(request.user, book),
        "statuses": ShelfEntry.Status.choices,
        "my_review": my_review,
        "review_form": ReviewForm(instance=my_review),
        "reviews": social_services.reviews_for_book(book),
        "rating": social_services.rating_summary(book),
        "following_ids": social_services.following_ids(request.user),
    }
    return render(request, "books/book_detail.html", context)

  
def search(request):
    query = request.GET.get("q", "").strip()
    results = Book.objects.none()

    if query:
        matching = Book.objects.filter(
            Q(title__icontains=query) | Q(authors__name__icontains=query)
        ).values("pk")
        results = (
            Book.objects.filter(pk__in=matching)
            .annotate(avg_rating=Avg("reviews__rating"))
            .order_by("title")
            .prefetch_related("authors")
        )
    paginator = Paginator(results, 20) # paginator splits long list of results into pages
    page = paginator.get_page(request.GET.get("page")) #pick the page number from the address (?page=2)

    return render(request, "books/search.html", {"query": query, "page": page})

def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    books = (
        Book.objects.filter(authors=author)
        .order_by("title")
    ) 
    paginator = Paginator(books, 20) # paginator splits long list of results into pages
    page = paginator.get_page(request.GET.get("page"))
    return render(
            request,
            "books/author_detail.html",
            {"author":author, "page" : page},
        )