from django.shortcuts import render, get_object_or_404
from .models import Book

# Create your views here.

def home(request):
    books = Book.objects.order_by("source_id")[:12]
    return render(request, "books/home.html", {"books": books})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, "books/book_detail.html", {"book": book})


