from rest_framework import permissions
from .models import UserRole
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


# ============================================================
# DRF Permission Classes (preserved from original codebase)
# ============================================================

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == UserRole.ADMIN)


class IsGuard(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == UserRole.GUARD)


class IsResident(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == UserRole.RESIDENT)


class IsAdminOrGuardReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role == UserRole.ADMIN:
            return True
        if request.user.role == UserRole.GUARD and request.method in permissions.SAFE_METHODS:
            return True
        return False


class IsAdminOrResidentReadOnlyOwn(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role == UserRole.ADMIN:
            return True
        if request.user.role == UserRole.RESIDENT:
            return True  # Let get_queryset and object permissions handle the rest
        return False


# ============================================================
# Django View Decorators  (for server-side rendered views)
# ============================================================

def role_required(allowed_role):
    """Decorator that combines @login_required with a role check."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role != allowed_role:
                return HttpResponseForbidden(
                    "You do not have permission to access this page."
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Shortcut: @login_required + role == Admin."""
    return role_required(UserRole.ADMIN)(view_func)


def guard_required(view_func):
    """Shortcut: @login_required + role == Guard."""
    return role_required(UserRole.GUARD)(view_func)


def resident_required(view_func):
    """Shortcut: @login_required + role == Resident."""
    return role_required(UserRole.RESIDENT)(view_func)
