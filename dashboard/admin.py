# Register your models here.
from django.contrib import admin
from .models import Farmer, LandDetail, BankDetail

class LandInline(admin.StackedInline):
    model = LandDetail
    extra = 0
    can_delete = False

class BankInline(admin.StackedInline):
    model = BankDetail
    extra = 0
    can_delete = False

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ("full_name","phone_number","aadhar_number","district","village")
    search_fields = ("full_name","aadhar_number","phone_number","email")
    inlines = [LandInline, BankInline]

admin.site.register(LandDetail)
admin.site.register(BankDetail)

