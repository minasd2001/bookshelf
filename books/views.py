from django.shortcuts import render, get_object_or_404
from .models import Book
from django.core.paginator import Paginator
from django.db.models import Q # for multiple field search
# Create your views here.

def home(request):
    books = Book.objects.order_by("source_id")[:12]
    return render(request, "books/home.html", {"books": books})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, "books/book_detail.html", {"book": book})

  
def search(request):
    query = request.GET.get("q", "").strip()
    results = Book.objects.none()

    if query:
        results = (
            Book.objects
            .filter(Q(title__icontains=query) | Q(authors__name__icontains=query))
            .distinct()
            .order_by("title")
            .prefetch_related("authors")
        )
    paginator = Paginator(results, 20) # paginator splits long list of results into pages
    page = paginator.get_page(request.GET.get("page")) #pick the page number from the address (?page=2)

    return render(request, "books/search.html", {"query": query, "page": page})
