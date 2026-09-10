from django.contrib import admin
from .models import Flat, Resident, MaintenanceRequest, Visitor, Payment


@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    list_display = ("flat_number", "block", "floor", "flat_type", "owner_name", "base_maintenance_amount", "is_active")
    list_filter = ("block", "flat_type", "is_active")
    search_fields = ("flat_number", "block", "owner_name")


@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ("username", "full_name", "role", "flat", "status", "is_active")
    list_filter = ("role", "status", "is_active")
    search_fields = ("username", "full_name")


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ("pk", "flat", "category", "status", "assigned_to", "created_at")
    list_filter = ("status", "category")
    search_fields = ("flat__flat_number", "description")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("pk", "flat", "charge_type", "amount", "status", "billing_month", "paid_at")
    list_filter = ("status", "charge_type")
    search_fields = ("flat__flat_number", "description")


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "target_flat", "purpose", "status", "check_in_time", "exit_time")
    list_filter = ("status", "purpose")
    search_fields = ("full_name", "contact_number", "vehicle_number")
