# app/serializers.py
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from .models import UserProfile, SubsidyApproval

class UserProfileSerializer(serializers.ModelSerializer):
    # Read-only fields from the related user model
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email_address = serializers.EmailField(source="user.email_address", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)
    mobile_number = PhoneNumberField(source="user.mobile_number", read_only=True)

    # Optional image upload field (editable)

    class Meta:
        model = UserProfile
        fields = [
            "aadhaar_number",
            "state",
            "district",
            "taluka",
            "village",
            "address",
            "photo",
            "land_size",
            "unit",
            "soil_type",
            "ownership_type",
            "land_proof",
            "bank_account_number",
            "ifsc_code",
            "bank_name",
            "pan_card",
            "aadhaar_card",
            "full_name",
            "email_address",
            "role",
            "mobile_number",
        ]
        
        read_only_fields = ["user"]


class OfficerUserProfileSerializer(UserProfileSerializer):
    profile_id = serializers.IntegerField(source="id", read_only=True)
    subsidy_status = serializers.CharField(source="subsidy_approval.status", read_only=True)
    subsidy_remarks = serializers.CharField(
        source="subsidy_approval.remarks",
        read_only=True,
        allow_null=True,
        allow_blank=True,
    )
    verified_at = serializers.DateTimeField(
        source="subsidy_approval.verified_at",
        read_only=True,
        allow_null=True,
    )
    verified_by = serializers.SerializerMethodField()
    verified_by_id = serializers.IntegerField(
        source="subsidy_approval.verified_by_id",
        read_only=True,
    )

    class Meta(UserProfileSerializer.Meta):
        fields = [
            "profile_id",
            *UserProfileSerializer.Meta.fields,
            "subsidy_status",
            "subsidy_remarks",
            "verified_at",
            "verified_by",
            "verified_by_id",
        ]

    def get_verified_by(self, obj):
        approval = getattr(obj, "subsidy_approval", None)
        if approval and approval.verified_by:
            return approval.verified_by.full_name
        return None


class SubsidyApprovalActionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            SubsidyApproval.STATUS_APPROVED,
            SubsidyApproval.STATUS_REJECTED,
        ]
    )
    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=1000,
    )

    def validate_status(self, value):
        if value == SubsidyApproval.STATUS_PENDING:
            raise serializers.ValidationError("Use approve or reject for officer actions.")
        return value
