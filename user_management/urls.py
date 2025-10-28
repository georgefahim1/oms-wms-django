# user_management/urls.py

from django.urls import path
from .views import (
    UserCreateView, AttendanceView, OrderCreateListView, 
    OrderRetrieveUpdateStatusView, OrderDispatchAssignmentView,
    DeliveryPersonnelListView, GPSTrackingView, ProofOfExecutionView, 
    SalesVisitPlanCreateUpdateListView, SalesVisitPlanRetrieveUpdateDestroyView,
    TimeOffRequestView, TimeOffApprovalView, StaffStatusOverrideView,
    MLMPrivateTaskListView, MLMPrivateTaskRetrieveUpdateDestroyView,
    KPIView, StaffStatusAuditListView, GPSTrackingHistoryListView,
    NonPaginatedUserListView # <-- NEW IMPORT
)

urlpatterns = [
    # Authentication/User Creation
    path('users/register/', UserCreateView.as_view(), name='user-register'),
    
    # --- FINAL FIX: Employee List (Non-Paginated) ---
    path('users/employee-list/', NonPaginatedUserListView.as_view(), name='employee-list-non-paginated'),
    
    # Time & Attendance API
    path('attendance/', AttendanceView.as_view(), name='user-attendance'),
    
    # ... (All other existing paths remain unchanged) ...
    path('orders/', OrderCreateListView.as_view(), name='order-list-create'),
    path('orders/status/<uuid:id>/', OrderRetrieveUpdateStatusView.as_view(), name='order-retrieve-update-status'),
    path('orders/dispatch/<uuid:id>/', OrderDispatchAssignmentView.as_view(), name='order-dispatch-assign'),
    path('personnel/delivery/', DeliveryPersonnelListView.as_view(), name='delivery-personnel-list'),
    path('tracking/', GPSTrackingView.as_view(), name='gps-tracking-create'),
    path('proofs/upload/', ProofOfExecutionView.as_view(), name='proof-upload'),
    path('sales/plans/', SalesVisitPlanCreateUpdateListView.as_view(), name='sales-plan-list-create'),
    path('sales/plans/<int:id>/', SalesVisitPlanRetrieveUpdateDestroyView.as_view(), name='sales-plan-retrieve-update'),
    path('hr/time-off/', TimeOffRequestView.as_view(), name='time-off-list-create'),
    path('hr/time-off/<int:id>/approve/', TimeOffApprovalView.as_view(), name='time-off-approve'),
    path('managers/status/override/', StaffStatusOverrideView.as_view(), name='manager-status-override'),
    path('manager/tasks/', MLMPrivateTaskListView.as_view(), name='mlm-task-list-create'),
    path('manager/tasks/<uuid:id>/', MLMPrivateTaskRetrieveUpdateDestroyView.as_view(), name='mlm-task-retrieve-update'),
    path('analytics/kpis/', KPIView.as_view(), name='analytics-kpis'),
]