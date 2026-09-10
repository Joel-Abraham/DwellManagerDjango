from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


# ============================================================
# ENUMS / CHOICES
# ============================================================

class UserRole(models.TextChoices):
    RESIDENT = "Resident", "Resident"
    GUARD = "Guard", "Guard"
    ADMIN = "Admin", "Admin"


class FlatType(models.TextChoices):
    BHK1 = "1BHK", "1 BHK"
    BHK2 = "2BHK", "2 BHK"
    BHK3 = "3BHK", "3 BHK"
    BHK4 = "4BHK", "4 BHK"
    PENTHOUSE = "Penthouse", "Penthouse"
    STUDIO = "Studio", "Studio"


class ResidentStatus(models.TextChoices):
    ACTIVE = "Active", "Active"
    INACTIVE = "Inactive", "Inactive"
    MOVED_OUT = "Moved-out", "Moved-out"


class MaintenanceCategory(models.TextChoices):
    PLUMBING = "plumbing", "Plumbing"
    ELECTRICAL = "electrical", "Electrical"
    HVAC = "hvac", "HVAC / Air Conditioning"
    CARPENTRY = "carpentry", "Carpentry"
    PAINTING = "painting", "Painting"
    PEST_CONTROL = "pest_control", "Pest Control"
    APPLIANCE = "appliance", "Appliance Repair"
    ELEVATOR = "elevator", "Elevator"
    COMMON_AREA = "common_area", "Common Area / Housekeeping"
    WATER_SUPPLY = "water_supply", "Water Supply"
    INTERNET = "internet", "Internet / Cabling"
    SECURITY = "security", "Security"
    OTHER = "other", "Other"


class MaintenanceStatus(models.TextChoices):
    PENDING = "Pending", "Pending"
    ASSIGNED = "Assigned", "Assigned"
    IN_PROGRESS = "In Progress", "In Progress"
    COMPLETED = "Completed", "Completed"


class VisitorPurpose(models.TextChoices):
    DELIVERY = "Delivery", "Delivery"
    GUEST = "Guest", "Guest"
    SERVICE = "Service/Maintenance", "Service/Maintenance"
    OTHER = "Other", "Other"


class VisitorStatus(models.TextChoices):
    INSIDE = "Inside", "Inside"
    CHECKED_OUT = "Checked-Out", "Checked-Out"


class VehicleType(models.TextChoices):
    CAR = "Car", "Car"
    BIKE = "Bike", "Bike"
    NONE = "None", "None"


class ChargeType(models.TextChoices):
    BASE_MAINTENANCE = "Base Maintenance", "Base Maintenance"
    ADDITIONAL_CHARGE = "Additional Charge", "Additional Charge"


class PaymentStatus(models.TextChoices):
    UNPAID = "Unpaid", "Unpaid"
    PAID = "Paid", "Paid"


class PaymentMethod(models.TextChoices):
    UPI = "UPI", "UPI"
    NET_BANKING = "Net Banking", "Net Banking"
    CASH = "Cash", "Cash"


# ============================================================
# FLAT
# ============================================================

class Flat(models.Model):
    flat_number = models.CharField(max_length=20)
    block = models.CharField(max_length=50)
    floor = models.PositiveIntegerField()
    flat_type = models.CharField(max_length=20, choices=FlatType.choices)
    owner_name = models.CharField(max_length=100)
    base_maintenance_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    is_active = models.BooleanField(default=True)
    manually_marked_occupied = models.BooleanField(
        default=False,
        help_text="Use this if a resident is living here but doesn't have a portal account yet.",
    )

    class Meta:
        unique_together = ["flat_number", "block"]
        ordering = ["block", "flat_number"]

    def __str__(self):
        return f"{self.block} - {self.flat_number}"

    @property
    def is_occupied(self):
        """True when at least one Active resident is linked, or manually marked."""
        has_active_resident = self.residents.filter(
            role=UserRole.RESIDENT,
            status=ResidentStatus.ACTIVE,
        ).exists()
        return has_active_resident or self.manually_marked_occupied


# ============================================================
# CUSTOM USER  (AUTH_USER_MODEL = 'api.Resident')
# ============================================================

class ResidentManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        user = self.model(username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)
        return self.create_user(username, password, **extra_fields)


class Resident(AbstractBaseUser, PermissionsMixin):
    flat = models.ForeignKey(
        Flat,
        on_delete=models.RESTRICT,
        related_name="residents",
        null=True,
        blank=True,
    )
    username = models.CharField(max_length=50, unique=True, db_index=True)
    full_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    role = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.RESIDENT
    )
    status = models.CharField(
        max_length=20,
        choices=ResidentStatus.choices,
        default=ResidentStatus.ACTIVE,
    )
    move_in_date = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = ResidentManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.username


# ============================================================
# MAINTENANCE REQUEST  (replaces old Complaint model)
# ============================================================

class MaintenanceRequest(models.Model):
    flat = models.ForeignKey(
        Flat,
        on_delete=models.RESTRICT,
        related_name="maintenance_requests",
    )
    category = models.CharField(max_length=30, choices=MaintenanceCategory.choices)
    description = models.TextField(max_length=500)
    status = models.CharField(
        max_length=20,
        choices=MaintenanceStatus.choices,
        default=MaintenanceStatus.PENDING,
    )
    assigned_to = models.CharField(max_length=100, null=True, blank=True)
    scheduled_date = models.DateField(null=True, blank=True)
    fee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Request #{self.pk} - {self.get_category_display()}"


# ============================================================
# PAYMENT  (unified billing: base maintenance + additional charges)
# ============================================================

class Payment(models.Model):
    flat = models.ForeignKey(
        Flat,
        on_delete=models.RESTRICT,
        related_name="payments",
    )
    charge_type = models.CharField(
        max_length=30,
        choices=ChargeType.choices,
        default=ChargeType.BASE_MAINTENANCE,
    )
    source_request = models.ForeignKey(
        MaintenanceRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="charges",
    )
    billing_month = models.CharField(max_length=20)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    description = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        null=True,
        blank=True,
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    receipt_ref = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.flat} - {self.get_charge_type_display()} - {self.billing_month}"


# ============================================================
# VISITOR
# ============================================================

class Visitor(models.Model):
    full_name = models.CharField(max_length=60)
    contact_number = models.CharField(max_length=15)
    target_flat = models.ForeignKey(
        Flat,
        on_delete=models.RESTRICT,
        related_name="visitors",
    )
    purpose = models.CharField(max_length=30, choices=VisitorPurpose.choices)
    vehicle_number = models.CharField(max_length=20, null=True, blank=True)
    vehicle_type = models.CharField(
        max_length=10,
        choices=VehicleType.choices,
        null=True,
        blank=True,
    )
    check_in_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=VisitorStatus.choices,
        default=VisitorStatus.INSIDE,
    )

    class Meta:
        ordering = ["-check_in_time"]

    def __str__(self):
        return self.full_name
