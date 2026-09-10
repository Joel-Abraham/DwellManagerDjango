from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Sum
from decimal import Decimal

from .models import (
    Flat,
    Resident,
    MaintenanceRequest,
    Visitor,
    Payment,
    UserRole,
    MaintenanceStatus,
    PaymentStatus,
    VisitorStatus,
    ChargeType,
    ResidentStatus,
)
from .forms import (
    LoginForm,
    FlatForm,
    ResidentForm,
    MaintenanceRequestForm,
    MaintenanceAssignForm,
    VisitorCheckInForm,
)
from .permissions import admin_required, guard_required, resident_required


# ============================================================
# AUTH VIEWS
# ============================================================

def login_view(request):
    """Django session login — replaces JWT-based SPA login."""
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return _redirect_by_role(user)
            else:
                messages.error(request, "Invalid username or password.")

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


def _redirect_by_role(user):
    if user.role == UserRole.ADMIN:
        return redirect("admin_dashboard")
    elif user.role == UserRole.GUARD:
        return redirect("guard_dashboard")
    elif user.role == UserRole.RESIDENT:
        return redirect("resident_dashboard")
    return redirect("login")


# ============================================================
# ADMIN — DASHBOARD
# ============================================================

@admin_required
def admin_dashboard(request):
    context = {
        "total_flats": Flat.objects.filter(is_active=True).count(),
        "total_residents": Resident.objects.filter(
            role=UserRole.RESIDENT, status=ResidentStatus.ACTIVE
        ).count(),
        "pending_requests": MaintenanceRequest.objects.filter(
            status=MaintenanceStatus.PENDING
        ).count(),
        "visitors_inside": Visitor.objects.filter(
            status=VisitorStatus.INSIDE
        ).count(),
        "total_unpaid": Payment.objects.filter(
            status=PaymentStatus.UNPAID
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00"),
    }
    return render(request, "admin/dashboard.html", context)


# ============================================================
# ADMIN — FLAT MANAGEMENT
# ============================================================

@admin_required
def admin_flat_list(request):
    flats = Flat.objects.all().order_by("block", "flat_number")
    return render(request, "admin/flat_list.html", {"flats": flats})


@admin_required
def admin_flat_create(request):
    form = FlatForm()
    if request.method == "POST":
        form = FlatForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Flat created successfully.")
            return redirect("admin_flat_list")
    return render(
        request, "admin/flat_form.html", {"form": form, "title": "Create Flat"}
    )


@admin_required
def admin_flat_edit(request, flat_id):
    flat = get_object_or_404(Flat, pk=flat_id)
    form = FlatForm(instance=flat)
    if request.method == "POST":
        form = FlatForm(request.POST, instance=flat)
        if form.is_valid():
            form.save()
            messages.success(request, "Flat updated successfully.")
            return redirect("admin_flat_list")
    return render(
        request,
        "admin/flat_form.html",
        {"form": form, "title": "Edit Flat", "flat": flat},
    )


@admin_required
def admin_flat_deactivate(request, flat_id):
    flat = get_object_or_404(Flat, pk=flat_id)
    if request.method == "POST":
        flat.is_active = False
        flat.save()
        messages.success(request, f"Flat {flat} deactivated.")
    return redirect("admin_flat_list")


# ============================================================
# ADMIN — RESIDENT MANAGEMENT
# ============================================================

@admin_required
def admin_resident_list(request):
    residents = Resident.objects.filter(role=UserRole.RESIDENT).select_related("flat")

    # Filtering
    flat_id = request.GET.get("flat")
    block = request.GET.get("block")
    status_filter = request.GET.get("status")

    if flat_id:
        residents = residents.filter(flat_id=flat_id)
    if block:
        residents = residents.filter(flat__block=block)
    if status_filter:
        residents = residents.filter(status=status_filter)

    blocks = (
        Flat.objects.values_list("block", flat=True).distinct().order_by("block")
    )
    flats = Flat.objects.filter(is_active=True).order_by("block", "flat_number")

    return render(
        request,
        "admin/resident_list.html",
        {
            "residents": residents,
            "blocks": blocks,
            "flats": flats,
            "current_flat": flat_id,
            "current_block": block,
            "current_status": status_filter,
            "status_choices": ResidentStatus.choices,
        },
    )


@admin_required
def admin_resident_create(request):
    form = ResidentForm()
    if request.method == "POST":
        form = ResidentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Resident created successfully.")
            return redirect("admin_resident_list")
    return render(
        request,
        "admin/resident_form.html",
        {"form": form, "title": "Create Resident"},
    )


@admin_required
def admin_resident_edit(request, resident_id):
    resident = get_object_or_404(Resident, pk=resident_id, role=UserRole.RESIDENT)
    form = ResidentForm(instance=resident)
    if request.method == "POST":
        form = ResidentForm(request.POST, instance=resident)
        if form.is_valid():
            form.save()
            messages.success(request, "Resident updated successfully.")
            return redirect("admin_resident_list")
    return render(
        request,
        "admin/resident_form.html",
        {"form": form, "title": "Edit Resident", "resident": resident},
    )


@admin_required
def admin_resident_deactivate(request, resident_id):
    resident = get_object_or_404(Resident, pk=resident_id, role=UserRole.RESIDENT)
    if request.method == "POST":
        resident.status = ResidentStatus.INACTIVE
        resident.save()
        messages.success(request, f"Resident {resident.full_name} deactivated.")
    return redirect("admin_resident_list")


# ============================================================
# ADMIN — RESIDENT PAYMENT DETAILS
# ============================================================

@admin_required
def admin_resident_payments(request, resident_id):
    resident = get_object_or_404(Resident, pk=resident_id, role=UserRole.RESIDENT)
    if not resident.flat:
        messages.warning(request, "This resident has no flat assigned.")
        return redirect("admin_resident_list")

    payments = Payment.objects.filter(flat=resident.flat).order_by("created_at")

    # Calculate running outstanding balance server-side
    running_balance = Decimal("0.00")
    payment_rows = []
    for p in payments:
        if p.status == PaymentStatus.UNPAID:
            running_balance += p.amount
        row = {
            "payment": p,
            "running_balance": running_balance,
        }
        payment_rows.append(row)

    total_outstanding = Payment.objects.filter(
        flat=resident.flat, status=PaymentStatus.UNPAID
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    return render(
        request,
        "admin/resident_payments.html",
        {
            "resident": resident,
            "payment_rows": payment_rows,
            "total_outstanding": total_outstanding,
        },
    )


# ============================================================
# ADMIN — MAINTENANCE ASSIGNMENT
# ============================================================

@admin_required
def admin_maintenance_list(request):
    requests_qs = MaintenanceRequest.objects.select_related("flat").all()
    return render(
        request,
        "admin/maintenance_list.html",
        {"maintenance_requests": requests_qs},
    )


@admin_required
def admin_maintenance_assign(request, request_id):
    maint_request = get_object_or_404(MaintenanceRequest, pk=request_id)

    if maint_request.status != MaintenanceStatus.PENDING:
        messages.error(request, "Only Pending requests can be assigned.")
        return redirect("admin_maintenance_list")

    form = MaintenanceAssignForm()
    if request.method == "POST":
        form = MaintenanceAssignForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Re-fetch inside transaction to check status
                    maint_request = MaintenanceRequest.objects.select_for_update().get(
                        pk=request_id
                    )
                    if maint_request.status != MaintenanceStatus.PENDING:
                        raise ValueError("Request is no longer Pending.")

                    maint_request.assigned_to = form.cleaned_data["assigned_to"]
                    maint_request.scheduled_date = form.cleaned_data["scheduled_date"]

                    fee = form.cleaned_data.get("fee_amount") or Decimal("0.00")
                    maint_request.fee_amount = fee if fee > 0 else None
                    maint_request.status = MaintenanceStatus.ASSIGNED
                    maint_request.save()

                    # Create AdditionalCharge (Payment) if fee > 0
                    if fee > 0:
                        Payment.objects.create(
                            flat=maint_request.flat,
                            charge_type=ChargeType.ADDITIONAL_CHARGE,
                            source_request=maint_request,
                            billing_month=timezone.now().strftime("%B %Y"),
                            amount=fee,
                            description=f"Maintenance Fee – (Request #{maint_request.pk})",
                            status=PaymentStatus.UNPAID,
                        )

                messages.success(request, "Request assigned successfully.")
                return redirect("admin_maintenance_list")

            except ValueError as e:
                messages.error(request, str(e))
            except Exception:
                messages.error(request, "Assignment failed. Please try again.")

    return render(
        request,
        "admin/maintenance_assign.html",
        {"form": form, "maint_request": maint_request},
    )


# ============================================================
# GUARD — DASHBOARD
# ============================================================

@guard_required
def guard_dashboard(request):
    form = VisitorCheckInForm()
    inside_visitors = Visitor.objects.filter(
        status=VisitorStatus.INSIDE
    ).select_related("target_flat")

    if request.method == "POST":
        form = VisitorCheckInForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Visitor checked in successfully.")
            return redirect("guard_dashboard")

    return render(
        request,
        "guard/dashboard.html",
        {"form": form, "inside_visitors": inside_visitors},
    )


# ============================================================
# GUARD — VISITOR CHECKOUT
# ============================================================

@guard_required
def guard_visitor_checkout(request, visitor_id):
    visitor = get_object_or_404(Visitor, pk=visitor_id)

    if visitor.status != VisitorStatus.INSIDE:
        messages.error(request, "Visitor already checked out")
        return redirect("guard_dashboard")

    if request.method == "POST":
        visitor.exit_time = timezone.now()
        visitor.status = VisitorStatus.CHECKED_OUT
        visitor.save()
        messages.success(request, f"{visitor.full_name} checked out successfully.")

    return redirect("guard_dashboard")


# ============================================================
# GUARD — VISITOR LOG
# ============================================================

@guard_required
def guard_visitor_log(request):
    visitors = Visitor.objects.select_related("target_flat").all()

    # Search filters
    search = request.GET.get("search", "").strip()
    date_filter = request.GET.get("date", "").strip()

    if search:
        visitors = visitors.filter(
            Q(full_name__icontains=search)
            | Q(contact_number__icontains=search)
            | Q(target_flat__flat_number__icontains=search)
            | Q(target_flat__block__icontains=search)
            | Q(vehicle_number__icontains=search)
        )
    if date_filter:
        visitors = visitors.filter(check_in_time__date=date_filter)

    return render(
        request,
        "guard/visitor_log.html",
        {"visitors": visitors, "search": search, "date_filter": date_filter},
    )


# ============================================================
# RESIDENT — DASHBOARD
# ============================================================

@resident_required
def resident_dashboard(request):
    resident = request.user
    if not resident.flat:
        return render(request, "resident/dashboard.html", {"no_flat": True})

    flat = resident.flat
    unpaid_count = Payment.objects.filter(
        flat=flat, status=PaymentStatus.UNPAID
    ).count()
    total_due = Payment.objects.filter(
        flat=flat, status=PaymentStatus.UNPAID
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    pending_requests = MaintenanceRequest.objects.filter(
        flat=flat, status=MaintenanceStatus.PENDING
    ).count()

    return render(
        request,
        "resident/dashboard.html",
        {
            "flat": flat,
            "unpaid_count": unpaid_count,
            "total_due": total_due,
            "pending_requests": pending_requests,
        },
    )


# ============================================================
# RESIDENT — BILLING  (data isolation: always scoped to own flat)
# ============================================================

@resident_required
def resident_billing(request):
    resident = request.user
    if not resident.flat:
        messages.warning(request, "No flat assigned to your account.")
        return redirect("resident_dashboard")

    flat = resident.flat
    payments = Payment.objects.filter(flat=flat)

    outstanding = payments.filter(status=PaymentStatus.UNPAID)
    paid = payments.filter(status=PaymentStatus.PAID)

    # Server-side total using Decimal
    total_due = outstanding.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    return render(
        request,
        "resident/billing.html",
        {
            "outstanding": outstanding,
            "paid": paid,
            "total_due": total_due,
            "flat": flat,
        },
    )


# ============================================================
# RESIDENT — PAY CHARGE  (data isolation + atomic)
# ============================================================

@resident_required
def resident_pay_charge(request, charge_id):
    """
    CRITICAL: The lookup includes flat=request.user.flat so a resident
    can never pay another flat's charge by manipulating the URL.
    """
    resident = request.user
    if not resident.flat:
        messages.warning(request, "No flat assigned to your account.")
        return redirect("resident_dashboard")

    # Scoped lookup — returns 404 if charge belongs to another flat
    payment = get_object_or_404(Payment, pk=charge_id, flat=resident.flat)

    if payment.status == PaymentStatus.PAID:
        messages.error(request, "This charge has already been paid.")
        return redirect("resident_billing")

    if request.method == "POST":
        payment_method = request.POST.get("payment_method", "UPI")
        with transaction.atomic():
            # Re-fetch with lock
            payment = Payment.objects.select_for_update().get(
                pk=charge_id, flat=resident.flat
            )
            if payment.status == PaymentStatus.PAID:
                messages.error(request, "This charge has already been paid.")
                return redirect("resident_billing")

            payment.status = PaymentStatus.PAID
            payment.paid_at = timezone.now()
            payment.payment_method = payment_method
            payment.receipt_ref = f"RCPT-{payment.pk}-{int(timezone.now().timestamp())}"
            payment.save()

        messages.success(request, "Payment successful!")
        return render(
            request,
            "resident/receipt.html",
            {"payment": payment, "resident": resident},
        )

    return render(
        request,
        "resident/pay_charge.html",
        {"payment": payment},
    )


# ============================================================
# RESIDENT — REQUEST MAINTENANCE
# ============================================================

@resident_required
def resident_request_maintenance(request):
    """
    Flat is assigned server-side from request.user.flat.
    The form does NOT include a flat field; any client-submitted flat value is ignored.
    """
    resident = request.user
    if not resident.flat:
        messages.warning(request, "No flat assigned to your account.")
        return redirect("resident_dashboard")

    form = MaintenanceRequestForm()
    if request.method == "POST":
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            maint_req = form.save(commit=False)
            maint_req.flat = resident.flat  # Server-side assignment
            maint_req.save()
            messages.success(request, "Maintenance request submitted.")
            return redirect("resident_my_requests")

    return render(
        request,
        "resident/maintenance_form.html",
        {"form": form},
    )


# ============================================================
# RESIDENT — MY REQUESTS  (data isolation)
# ============================================================

@resident_required
def resident_my_requests(request):
    resident = request.user
    if not resident.flat:
        messages.warning(request, "No flat assigned to your account.")
        return redirect("resident_dashboard")

    requests_qs = MaintenanceRequest.objects.filter(flat=resident.flat)

    # Prefetch associated charges
    request_data = []
    for mreq in requests_qs:
        charges = Payment.objects.filter(source_request=mreq, flat=resident.flat)
        request_data.append({"request": mreq, "charges": charges})

    return render(
        request,
        "resident/my_requests.html",
        {"request_data": request_data},
    )


# ============================================================
# DRF VIEWSETS  (preserved for API backward compatibility)
# ============================================================

from rest_framework import viewsets, permissions, status as drf_status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (
    FlatSerializer,
    ResidentSerializer,
    MaintenanceRequestSerializer,
    VisitorSerializer,
    PaymentSerializer,
)
from .permissions import (
    IsAdmin,
    IsGuard,
    IsResident,
    IsAdminOrGuardReadOnly,
    IsAdminOrResidentReadOnlyOwn,
)


class FlatViewSet(viewsets.ModelViewSet):
    serializer_class = FlatSerializer
    permission_classes = [IsAdminOrGuardReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.ADMIN:
            return Flat.objects.all()
        elif user.role == UserRole.GUARD:
            return Flat.objects.filter(is_active=True)
        return Flat.objects.none()


class ResidentViewSet(viewsets.ModelViewSet):
    serializer_class = ResidentSerializer
    permission_classes = [IsAdminOrResidentReadOnlyOwn]

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.ADMIN:
            return Resident.objects.all()
        elif user.role == UserRole.RESIDENT:
            return Resident.objects.filter(pk=user.pk)
        return Resident.objects.none()


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [IsAdminOrResidentReadOnlyOwn]

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.ADMIN:
            return MaintenanceRequest.objects.all()
        elif user.role == UserRole.RESIDENT and user.flat:
            return MaintenanceRequest.objects.filter(flat=user.flat)
        return MaintenanceRequest.objects.none()


class VisitorViewSet(viewsets.ModelViewSet):
    serializer_class = VisitorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in [UserRole.ADMIN, UserRole.GUARD]:
            return Visitor.objects.all()
        return Visitor.objects.none()


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminOrResidentReadOnlyOwn]

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.ADMIN:
            return Payment.objects.all()
        elif user.role == UserRole.RESIDENT and user.flat:
            return Payment.objects.filter(flat=user.flat)
        return Payment.objects.none()
