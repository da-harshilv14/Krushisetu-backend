# app/urls.py
from django.urls import path
from .views import UserProfileView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("profile/", UserProfileView.as_view(), name="user-profile"),
]

