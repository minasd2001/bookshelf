from django.urls import path

from . import views

urlpatterns = [
    path("shelf/<int:book_id>/", views.shelf_set, name="shelf_set"),
    path("review/<int:book_id>/", views.review_save, name="review_save"),
    path("review/<int:book_id>/delete/", views.review_delete, name="review_delete"),
    path("follow/<str:username>/", views.follow_user ,name="follow_user" ),
    path("unfollow/<str:username>/", views.unfollow_user ,name="unfollow_user"),
    path("people/<str:username>/followers/", views.followers_list, name="followers_list"),
    path("people/<str:username>/following/", views.following_list, name="following_list"),
]