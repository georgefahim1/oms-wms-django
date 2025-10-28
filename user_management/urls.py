# user_management/urls.py

from django.urls import path
from .views import (
    UserCreateView, AttendanceView, OrderCreateListView, 
    OrderRetrieveUpdateStatusView, OrderDispatchAssignmentView,
    DeliveryPersonnelListView, GPSTrackingView, ProofOfExecutionView, 
    SalesVisitPlanCreateUpdateListView, SalesVisitPlanRetrieveUpdateDestroyView,
    TimeOffRequestView, TimeOffApprovalView, StaffStatusOverrideView,
    MLMPrivateTaskListView, MLMPrivateTaskRetrieveUpdateDestroyView,
    KPIView, StaffStatusAuditListView, GPSTrackingHistoryListView # NEW IMPORTS
)

urlpatterns = [
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
    
    # Sales Planning APIs
    path('sales/plans/', SalesVisitPlanCreateUpdateListView.as_view(), name='sales-plan-list-create'),
    path('sales/plans/<int:id>/', SalesVisitPlanRetrieveUpdateDestroyView.as_view(), name='sales-plan-retrieve-update'),

    # Time Off Management APIs
    path('hr/time-off/', TimeOffRequestView.as_view(), name='time-off-list-create'),
    path('hr/time-off/<int:id>/approve/', TimeOffApprovalView.as_view(), name='time-off-approve'),

    # Manager Status Override API
    path('managers/status/override/', StaffStatusOverrideView.as_view(), name='manager-status-override'),
    
    # MLM Private Task APIs
    path('manager/tasks/', MLMPrivateTaskListView.as_view(), name='mlm-task-list-create'),
    path('manager/tasks/<uuid:id>/', MLMPrivateTaskRetrieveUpdateDestroyView.as_view(), name='mlm-task-retrieve-update'),
    
    # KPI Dashboard API
    path('analytics/kpis/', KPIView.as_view(), name='analytics-kpis'),

    # NEW: Audit Log APIs (Phase IV, Step 17)
    path('audit/status/', StaffStatusAuditListView.as_view(), name='audit-status-list'),
    path('audit/gps/', GPSTrackingHistoryListView.as_view(), name='audit-gps-list'),
]