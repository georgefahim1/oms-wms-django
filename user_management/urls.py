# user_management/urls.py

from django.urls import path
from .views import UserCreateView, AttendanceView # Import the new view

urlpatterns = [
    # Authentication/User Creation
    path('users/register/', UserCreateView.as_view(), name='user-register'),

    # Time & Attendance API
    # POST to clock in, PUT to clock out, GET for status
    path('attendance/', AttendanceView.as_view(), name='user-attendance'),
]