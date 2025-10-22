# app/serializers.py
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from .models import UserProfile

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
