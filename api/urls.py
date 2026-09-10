from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Server-side views
    login_view,
    logout_view,
    admin_dashboard,
    admin_flat_list,
    admin_flat_create,
    admin_flat_edit,
    admin_flat_deactivate,
    admin_resident_list,
    admin_resident_create,
    admin_resident_edit,
    admin_resident_deactivate,
    admin_resident_payments,
    admin_maintenance_list,
    admin_maintenance_assign,
    guard_dashboard,
    guard_visitor_checkout,
    guard_visitor_log,
    resident_dashboard,
    resident_billing,
    resident_pay_charge,
    resident_request_maintenance,
    resident_my_requests,
    # DRF ViewSets
    FlatViewSet,
    ResidentViewSet,
    MaintenanceRequestViewSet,
    VisitorViewSet,
    PaymentViewSet,
)

# DRF router (preserved for API backward compatibility)
router = DefaultRouter()
router.register(r"flats", FlatViewSet, basename="flat")
router.register(r"residents", ResidentViewSet, basename="resident")
router.register(r"maintenance-requests", MaintenanceRequestViewSet, basename="maintenance-request")
router.register(r"visitors", VisitorViewSet, basename="visitor")
router.register(r"payments", PaymentViewSet, basename="payment")

# Server-side URL patterns
urlpatterns = [
    # Auth
    path("", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    # Admin — Dashboard
    path("admin/dashboard/", admin_dashboard, name="admin_dashboard"),
    # Admin — Flats
    path("admin/flats/", admin_flat_list, name="admin_flat_list"),
    path("admin/flats/create/", admin_flat_create, name="admin_flat_create"),
    path("admin/flats/<int:flat_id>/edit/", admin_flat_edit, name="admin_flat_edit"),
    path("admin/flats/<int:flat_id>/deactivate/", admin_flat_deactivate, name="admin_flat_deactivate"),
    # Admin — Residents
    path("admin/residents/", admin_resident_list, name="admin_resident_list"),
    path("admin/residents/create/", admin_resident_create, name="admin_resident_create"),
    path("admin/residents/<int:resident_id>/edit/", admin_resident_edit, name="admin_resident_edit"),
    path("admin/residents/<int:resident_id>/deactivate/", admin_resident_deactivate, name="admin_resident_deactivate"),
    path("admin/residents/<int:resident_id>/payments/", admin_resident_payments, name="admin_resident_payments"),
    # Admin — Maintenance
    path("admin/maintenance/", admin_maintenance_list, name="admin_maintenance_list"),
    path("admin/maintenance/<int:request_id>/assign/", admin_maintenance_assign, name="admin_maintenance_assign"),
    # Guard
    path("guard/", guard_dashboard, name="guard_dashboard"),
    path("guard/visitors/checkout/<int:visitor_id>/", guard_visitor_checkout, name="guard_visitor_checkout"),
    path("guard/visitors/log/", guard_visitor_log, name="guard_visitor_log"),
    # Resident
    path("resident/", resident_dashboard, name="resident_dashboard"),
    path("resident/billing/", resident_billing, name="resident_billing"),
    path("resident/billing/<int:charge_id>/pay/", resident_pay_charge, name="resident_pay_charge"),
    path("resident/maintenance/", resident_request_maintenance, name="resident_request_maintenance"),
    path("resident/maintenance/requests/", resident_my_requests, name="resident_my_requests"),
    # DRF API (backward compatible)
    path("api/v1/", include(router.urls)),
]
