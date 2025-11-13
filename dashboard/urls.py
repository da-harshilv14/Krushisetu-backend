# app/urls.py
from django.urls import path
from .views import (
    UserProfileView,
    OfficerPendingApprovalsListView,
    OfficerProfileReviewView,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path(
        "officer/pending/",
        OfficerPendingApprovalsListView.as_view(),
        name="officer-pending-profiles",
    ),
    path(
        "officer/profiles/<int:pk>/",
        OfficerProfileReviewView.as_view(),
        name="officer-profile-review",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)