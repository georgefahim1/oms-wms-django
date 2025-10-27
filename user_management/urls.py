# user_management/urls.py

from django.urls import path
from .views import UserCreateView, AttendanceView, OrderCreateListView, OrderRetrieveUpdateStatusView # Import new view

urlpatterns = [
    # Authentication/User Creation
    path('users/register/', UserCreateView.as_view(), name='user-register'),
    
    # Time & Attendance API
    path('attendance/', AttendanceView.as_view(), name='user-attendance'),
    
    # Order APIs
    path('orders/', OrderCreateListView.as_view(), name='order-list-create'),
    
    # NEW: Order Detail and Status Update
    # Expects a UUID in the URL, e.g., /api/orders/status/a1b2c3d4-e5f6.../
    path('orders/status/<uuid:id>/', OrderRetrieveUpdateStatusView.as_view(), name='order-retrieve-update-status'),
]