# user_management/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserAttendance, Order, OrderItem, GPSTrackingHistory

# ---------------------------------------------------------
# 1. Custom User Admin (To display UUID and custom fields)
# ---------------------------------------------------------
class UserAdmin(BaseUserAdmin):
    # Fields to display in the user list view
    list_display = ('email', 'first_name', 'last_name', 'role_key', 'reporting_manager', 'is_staff', 'is_active')
    # Fields that can be filtered
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role_key')
    # Fields to search
    search_fields = ('email', 'first_name', 'last_name')
    # Fields to order by
    ordering = ('email',)

    # Customize the fieldsets for the user detail page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'role_key', 'reporting_manager', 'pto_balance_days')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # We use email as the unique field, so remove the username field if present
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'username' in form.base_fields:
            del form.base_fields['username']
        return form

# ---------------------------------------------------------
# 2. Register Models
# ---------------------------------------------------------

# Unregister the default User model if it was already registered
# (Prevents issues with the custom model)
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# Register the Custom User model
admin.site.register(User, UserAdmin)

# Register the Attendance and Workflow Models
admin.site.register(UserAttendance)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(GPSTrackingHistory)