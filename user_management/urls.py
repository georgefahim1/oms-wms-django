# user_management/urls.py

from django.urls import path
from .views import UserCreateView, AttendanceView, OrderCreateListView # Import new view

urlpatterns = [
    # Authentication/User Creation
    path('users/register/', UserCreateView.as_view(), name='user-register'),

    # Time & Attendance API
    path('attendance/', AttendanceView.as_view(), name='user-attendance'),

    # NEW: Order APIs
    # POST to create a new order, GET to list orders
    path('orders/', OrderCreateListView.as_view(), name='order-list-create'),
]