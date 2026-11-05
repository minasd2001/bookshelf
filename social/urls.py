from django.urls import path

from . import views

urlpatterns = [
    path("shelf/<int:book_id>/", views.shelf_set, name="shelf_set"),
    path("review/<int:book_id>/", views.review_save, name="review_save"),
    path("review/<int:book_id>/delete/", views.review_delete, name="review_delete"),
]