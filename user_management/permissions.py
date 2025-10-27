# user_management/permissions.py

from rest_framework import permissions
from .models import UserRoles

class HasSystemRole(permissions.BasePermission):
    """
    Custom permission to only allow access if the user has one of the specified roles.
    Roles are passed in via the required_roles attribute on the view.
    """
    def has_permission(self, request, view):
        # If the user is an admin (is_superuser), grant permission immediately
        if request.user and request.user.is_superuser:
            return True

        # Check if the view specifies required roles
        required_roles = getattr(view, 'required_roles', None)

        # If no roles are required, deny access unless explicitly granted otherwise.
        if not required_roles:
            return False 

        # Check if the user is authenticated AND their role is in the required list
        if request.user and request.user.is_authenticated:
            return request.user.role_key in required_roles

        return False

# Pre-defined permission checks for common roles in the blueprint
class IsManagerOrAdmin(HasSystemRole):
    """Allows access only to High-Level Managers and Middle-Level Managers (and superusers)."""
    def has_permission(self, request, view):
        view.required_roles = [UserRoles.HLM, UserRoles.MLM]
        return super().has_permission(request, view)

class IsHLMOrAdmin(HasSystemRole):
    """Allows access only to High-Level Managers (and superusers)."""
    def has_permission(self, request, view):
        view.required_roles = [UserRoles.HLM]
        return super().has_permission(request, view)
    