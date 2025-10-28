# user_management/permissions.py

from rest_framework import permissions
from .models import UserRoles

class HasSystemRole(permissions.BasePermission):
    """
    Custom permission to only allow access if the user has one of the specified roles.
    """
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

class IsEmployeeManagerOrAdmin(HasSystemRole):
    def has_permission(self, request, view):
        view.required_roles = [UserRoles.HLM, UserRoles.MLM, UserRoles.EM]
        return super().has_permission(request, view)

# FIX: PTO APPROVAL PERMISSION (Required by TimeOffApprovalView)
class IsPTOManager(HasSystemRole):
    """Allows access only to HLM, MLM, and Employee Managers for PTO purposes."""
    def has_permission(self, request, view):
        view.required_roles = [UserRoles.HLM, UserRoles.MLM, UserRoles.EM]
        return super().has_permission(request, view)
        
# NEW DEFINITION: MLM Private Task Permission (Required by MLMPrivateTaskView)
class IsMLMOrHLM(HasSystemRole):
    """Allows access only to Middle-Level Managers and High-Level Managers."""
    def has_permission(self, request, view):
        view.required_roles = [UserRoles.HLM, UserRoles.MLM]
        return super().has_permission(request, view)