# user_management/urls.py

from django.urls import path
from .views import (
    UserCreateView, AttendanceView, OrderCreateListView, 
    OrderRetrieveUpdateStatusView, OrderDispatchAssignmentView,
    DeliveryPersonnelListView, GPSTrackingView,
    ProofOfExecutionView # CustomTokenObtainPairView is removed from the imports
)

urlpatterns = [
    # Custom Login Path (We are relying on the main project's urls.py for /api/token/ here)
    # path('users/login/', CustomTokenObtainPairView.as_view(), name='custom-login'),
    
    # Authentication/User Creation
    path('users/register/', UserCreateView.as_view(), name='user-register'),
    
    # Time & Attendance API
    path('attendance/', AttendanceView.as_view(), name='user-attendance'),
    
    # Order APIs
    path('orders/', OrderCreateListView.as_view(), name='order-list-create'),
    path('orders/status/<uuid:id>/', OrderRetrieveUpdateStatusView.as_view(), name='order-retrieve-update-status'),
    path('orders/dispatch/<uuid:id>/', OrderDispatchAssignmentView.as_view(), name='order-dispatch-assign'),
    
    # Personnel Lookup
    path('personnel/delivery/', DeliveryPersonnelListView.as_view(), name='delivery-personnel-list'),
    
    # GPS Tracking API (Mobile)
    path('tracking/', GPSTrackingView.as_view(), name='gps-tracking-create'),
    
    # Proof of Execution API (File Upload)
    path('proofs/upload/', ProofOfExecutionView.as_view(), name='proof-upload'),
]