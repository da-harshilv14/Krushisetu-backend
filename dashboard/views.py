# app/views.py
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.utils import timezone

from .models import UserProfile, SubsidyApproval
from .serializers import (
    UserProfileSerializer,
    OfficerUserProfileSerializer,
    SubsidyApprovalActionSerializer,
)
from .permissions import IsOfficerUser


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OfficerPendingApprovalsListView(generics.ListAPIView):
    serializer_class = OfficerUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOfficerUser]

    def get_queryset(self):
        return (
            UserProfile.objects.select_related("user", "subsidy_approval")
            .filter(user__role="farmer")
            .filter(subsidy_approval__status=SubsidyApproval.STATUS_PENDING)
            .order_by("user__full_name")
        )


class OfficerProfileReviewView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOfficerUser]
    lookup_field = "pk"

    def get_queryset(self):
        return (
            UserProfile.objects.select_related("user", "subsidy_approval")
            .filter(user__role="farmer")
        )

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return SubsidyApprovalActionSerializer
        return OfficerUserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        approval = instance.subsidy_approval
        approval.status = serializer.validated_data["status"]
        approval.remarks = serializer.validated_data.get("remarks") or ""
        approval.verified_by = request.user
        approval.verified_at = timezone.now()
        approval.save(update_fields=["status", "remarks", "verified_by", "verified_at"])

        output_serializer = OfficerUserProfileSerializer(
            instance, context=self.get_serializer_context()
        )
        return Response(output_serializer.data)
