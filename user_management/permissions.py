# user_management/permissions.py

from rest_framework import permissions
from .models import UserRoles

class HasSystemRole(permissions.BasePermission):
    # ... (Existing code)
    def has_permission(self, request, view):
        if request.user and request.user.is_superuser: return True
        required_roles = getattr(view, 'required_roles', None)
        if not required_roles: return False 
        if request.user and request.user.is_authenticated:
            return request.user.role_key in required_roles
        return False

class IsManagerOrAdmin(HasSystemRole):
    def has_permission(self, request, view):
        view.required_roles = [UserRoles.HLM, UserRoles.MLM]
        return super().has_permission(request, view)

class IsHLMOrAdmin(HasSystemRole):
    def has_permission(self, request, view):
        view.required_roles = [UserRoles.HLM]
        return super().has_permission(request, view)

class IsFrontDeskOrAdmin(HasSystemRole):
    def has_permission(self, request, view):
        view.required_roles = [UserRoles.FD]
        return super().has_permission(request, view)

# NEW: Permission for Step 13 (Employee Manager / Middle Manager / High Manager)
class IsEmployeeManagerOrAdmin(HasSystemRole):
    def has_permission(self, request, view):
        view.required_roles = [UserRoles.HLM, UserRoles.MLM, UserRoles.EM]
        return super().has_permission(request, view)