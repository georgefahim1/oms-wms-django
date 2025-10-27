# user_management/urls.py

from django.urls import path
from .views import UserCreateView

urlpatterns = [
    # POST /api/users/register/ - Protected by IsManagerOrAdmin permission
    path('users/register/', UserCreateView.as_view(), name='user-register'),
]