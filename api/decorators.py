from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def role_required(role):
    def check_role(user):
        if user.is_authenticated and getattr(user, 'role', None) == role:
            return True
        raise PermissionDenied
    return user_passes_test(check_role)

admin_required = role_required('Admin')
guard_required = role_required('Guard')
resident_required = role_required('Resident')
