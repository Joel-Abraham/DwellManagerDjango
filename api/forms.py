from django import forms
from django.core.validators import MinValueValidator
from decimal import Decimal

from .models import (
    Flat,
    Resident,
    MaintenanceRequest,
    Visitor,
    UserRole,
)


# ============================================================
# AUTH
# ============================================================

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Enter your username",
            "autocomplete": "username",
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "Enter your password",
            "autocomplete": "current-password",
        }),
    )


# ============================================================
# FLAT
# ============================================================

class FlatForm(forms.ModelForm):
    class Meta:
        model = Flat
        fields = [
            "flat_number",
            "block",
            "floor",
            "flat_type",
            "owner_name",
            "base_maintenance_amount",
        ]
        widgets = {
            "flat_number": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "e.g. A-101"}
            ),
            "block": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "e.g. Block A"}
            ),
            "floor": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "e.g. 1"}
            ),
            "flat_type": forms.Select(attrs={"class": "form-input"}),
            "owner_name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Owner full name"}
            ),
            "base_maintenance_amount": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0",
                }
            ),
        }

    def clean_base_maintenance_amount(self):
        amount = self.cleaned_data.get("base_maintenance_amount")
        if amount is not None and amount < 0:
            raise forms.ValidationError("Amount must not be negative.")
        return amount


# ============================================================
# RESIDENT
# ============================================================

class ResidentForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-input", "placeholder": "Leave blank to keep current"}
        ),
        help_text="Leave blank to keep current password (edit mode).",
    )

    class Meta:
        model = Resident
        fields = [
            "username",
            "full_name",
            "flat",
            "contact_number",
            "email",
            "move_in_date",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-input"}),
            "full_name": forms.TextInput(attrs={"class": "form-input"}),
            "flat": forms.Select(attrs={"class": "form-input"}),
            "contact_number": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "move_in_date": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["flat"].queryset = Flat.objects.filter(is_active=True)
        if not self.instance.pk:
            # New resident — password is required
            self.fields["password"].required = True
            self.fields["password"].help_text = "Required for new residents."

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = UserRole.RESIDENT
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


# ============================================================
# MAINTENANCE REQUEST  (resident-facing: only category + description)
# ============================================================

class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ["category", "description"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={
                "class": "form-input",
                "rows": 4,
                "placeholder": "Describe the issue in detail…",
                "maxlength": "500",
            }),
        }


# ============================================================
# MAINTENANCE ASSIGNMENT  (admin-facing)
# ============================================================

class MaintenanceAssignForm(forms.Form):
    assigned_to = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Technician / Company name"}
        ),
    )
    scheduled_date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-input", "type": "date"})
    )
    fee_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        widget=forms.NumberInput(
            attrs={
                "class": "form-input",
                "placeholder": "0.00",
                "step": "0.01",
                "min": "0",
            }
        ),
    )


# ============================================================
# VISITOR  (guard-facing check-in form)
# ============================================================

class VisitorCheckInForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = [
            "full_name",
            "contact_number",
            "target_flat",
            "purpose",
            "vehicle_number",
            "vehicle_type",
        ]
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Visitor full name"}
            ),
            "contact_number": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Contact number"}
            ),
            "target_flat": forms.Select(attrs={"class": "form-input"}),
            "purpose": forms.Select(attrs={"class": "form-input"}),
            "vehicle_number": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "e.g. KA01AB1234"}
            ),
            "vehicle_type": forms.Select(attrs={"class": "form-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target_flat"].queryset = Flat.objects.filter(is_active=True)
        self.fields["vehicle_number"].required = False
        self.fields["vehicle_type"].required = False
