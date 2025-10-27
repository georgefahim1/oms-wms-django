from django.urls import path
from .views import (
    UserCreateView, AttendanceView, OrderCreateListView, 
    OrderRetrieveUpdateStatusView, OrderDispatchAssignmentView,
    DeliveryPersonnelListView, GPSTrackingView, CustomTokenObtainPairView
)

urlpatterns = [
    # Authentication/User Creation
    path('users/login/', CustomTokenObtainPairView.as_view(), name='custom-login'),
    path('users/register/', UserCreateView.as_view(), name='user-register'),
    
    # Time & Attendance API
    path('attendance/', AttendanceView.as_view(), name='user-attendance'),
    
    # Order APIs
    path('orders/', OrderCreateListView.as_view(), name='order-list-create'),
    path('orders/status/<uuid:id>/', OrderRetrieveUpdateStatusView.as_view(), name='order-retrieve-update-status'),
    path('orders/dispatch/<uuid:id>/', OrderDispatchAssignmentView.as_view(), name='order-dispatch-assign'),
    
    # Personnel Lookup
    path('personnel/delivery/', DeliveryPersonnelListView.as_view(), name='delivery-personnel-list'),
    
    # NEW: GPS Tracking API (Mobile)
    path('tracking/', GPSTrackingView.as_view(), name='gps-tracking-create'),
]