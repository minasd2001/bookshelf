from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/edit/", views.profile_edit, name = "profile_edit"),
    path("profile/<str:username>/", views.profile_detail, name="profile_detail"),

]
