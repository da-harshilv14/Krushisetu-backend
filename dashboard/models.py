from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")

    # 🏡 Personal Info
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="documents/profile_photos/", blank=True, null=True)

    # 🏞️ Land Info
    land_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    soil_type = models.CharField(max_length=100, blank=True, null=True)
    ownership_type = models.CharField(max_length=20, blank=True, null=True)
    land_proof = models.FileField(upload_to="documents/land_proofs/", blank=True, null=True)

    # 🏦 Bank & ID Info
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=15, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    pan_card = models.FileField(upload_to="documents/pan_cards/", blank=True, null=True)
    aadhaar_card = models.FileField(upload_to="documents/aadhaar_cards/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.full_name}'s Profile"


class SubsidyApproval(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="subsidy_approval",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    remarks = models.TextField(blank=True, null=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="subsidy_reviews",
    )
    verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("-verified_at", "profile__user__full_name")

    def mark(self, status, officer=None, remarks=None):
        self.status = status
        self.remarks = remarks or ""
        if officer:
            self.verified_by = officer
            self.verified_at = timezone.now()
        self.save(update_fields=["status", "remarks", "verified_by", "verified_at"])

    def __str__(self):
        return f"SubsidyApproval({self.profile.user.full_name} - {self.status})"
