# user_management/permissions.py

from rest_framework import permissions
from .models import UserRoles

class HasSystemRole(permissions.BasePermission):
    """
    Custom permission to only allow access if the user has one of the specified roles.
    """
    def has_permission(self, request, view):
        # If the user is a superuser, grant permission immediately
        if request.user and request.user.is_superuser:
            return True
        
        required_roles = getattr(view, 'required_roles', None)
        
        if not required_roles:
            return False 
        
        if request.user and request.user.is_authenticated:
            return request.user.role_key in required_roles
            
        return False

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
        
class IsFrontDeskOrAdmin(HasSystemRole):
    """NEW: Allows access only to Front Desk personnel (and superusers)."""
    def has_permission(self, request, view):
        view.required_roles = [UserRoles.FD]
        return super().has_permission(request, view)