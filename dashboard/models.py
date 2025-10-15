from django.db import models

class Farmer(models.Model):
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    aadhar_number = models.CharField(max_length=12, unique=True)
    state = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    taluka = models.CharField(max_length=50)
    village = models.CharField(max_length=50)
    address = models.TextField()
    photo = models.ImageField(upload_to="profile_photos/", null=True, blank=True)

    def __str__(self):
        return self.full_name


class LandDetail(models.Model):
    farmer = models.OneToOneField(Farmer, on_delete=models.CASCADE, related_name="land")
    total_land_size = models.DecimalField(max_digits=10, decimal_places=2)
    soil_type = models.CharField(max_length=50)
    ownership_type = models.CharField(max_length=50)
    ownership_proof = models.FileField(upload_to="land_docs/", null=True, blank=True)


class BankDetail(models.Model):
    farmer = models.OneToOneField(Farmer, on_delete=models.CASCADE, related_name="bank")
    bank_account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=15)
    bank_name = models.CharField(max_length=100)
    pan_card = models.CharField(max_length=10)
    aadhar_card = models.CharField(max_length=12)

