# app/admin.py
from django.contrib import admin
from .models import UserProfile, SubsidyApproval

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "state", "district", "bank_name"]


@admin.register(SubsidyApproval)
class SubsidyApprovalAdmin(admin.ModelAdmin):
    list_display = ["profile", "status", "verified_by", "verified_at"]
    list_filter = ["status"]
    search_fields = [
        "profile__user__full_name",
        "profile__user__email_address",
        "profile__user__mobile_number",
    ]
