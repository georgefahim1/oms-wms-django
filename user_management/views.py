# user_management/views.py

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Count, Avg, F, ExpressionWrapper, fields, Sum, DecimalField
    
from .models import User, UserAttendance, Order, UserRoles, GPSTrackingHistory, ProofOfExecution, SalesVisitPlan, TimeOffRequest, StaffStatusAudit, MLMPrivateTask
from .serializers import (
    UserSerializer, UserAttendanceSerializer, OrderSerializer,
    OrderStatusUpdateSerializer, GPSTrackingSerializer, CustomTokenObtainPairSerializer, 
    ProofOfExecutionSerializer, SalesVisitPlanSerializer,
    TimeOffRequestSerializer, TimeOffApprovalSerializer, StaffStatusAuditSerializer,
    MLMPrivateTaskSerializer, StaffStatusAuditListSerializer # <-- NEW IMPORT
)
from .permissions import IsManagerOrAdmin, IsFrontDeskOrAdmin, IsEmployeeManagerOrAdmin, IsPTOManager, IsMLMOrHLM

# -------------------------------------------------------------------
# VIEWS (Existing Code)
# -------------------------------------------------------------------

# --- NEW: Non-Paginated User List View (FINAL FIX for dropdown) ---
class NonPaginatedUserListView(generics.ListAPIView):
    """
    Provides a simple list of all users, disabling pagination to simplify 
    frontend dropdown population.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    # CRITICAL FIX: Set pagination_class to None
    pagination_class = None 
    
    # Only return users who are employees (not just the superuser)
    def get_queryset(self):
        return User.objects.exclude(is_superuser=True).exclude(role_key__isnull=True)
# -------------------------------------------------------------------
# --- Register API (Protected) ---
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdmin] 
    
# --- Attendance API (Clock In/Out) (Existing) ---
class AttendanceView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        if UserAttendance.objects.filter(user=user, clock_out_time__isnull=True).exists(): return Response({'detail': 'User is already clocked in.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserAttendanceSerializer(data={'user': user.id})
        if serializer.is_valid():
            serializer.save(user=user, status='Available')
            return Response({'detail': 'Clocked in successfully.', 'record': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request):
        user = request.user
        try: open_record = UserAttendance.objects.get(user=user, clock_out_time__isnull=True)
        except UserAttendance.DoesNotExist: return Response({'detail': 'No active clock-in found.'}, status=status.HTTP_400_BAD_REQUEST)
        open_record.clock_out_time = timezone.now(); open_record.save() 
        serializer = UserAttendanceSerializer(open_record)
        return Response({'detail': 'Clocked out successfully.', 'record': serializer.data}, status=status.HTTP_200_OK)
    def get(self, request):
        user = request.user
        is_clocked_in = UserAttendance.objects.filter(user=user, clock_out_time__isnull=True).exists()
        return Response({'is_clocked_in': is_clocked_in}, status=status.HTTP_200_OK)

# --- Order Creation/List API (Existing) ---
class OrderCreateListView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer): serializer.save(order_creator=self.request.user)
    def get_queryset(self):
        user = self.request.user
        if user.role_key in [UserRoles.HLM, UserRoles.MLM, UserRoles.FD]: return Order.objects.all()
        return Order.objects.filter(order_creator=user)

# --- Order Routing & Status Update API (Existing) ---
class OrderRetrieveUpdateStatusView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    lookup_field = 'id'
    def get_serializer_class(self):
        if self.request.method == 'GET': return OrderSerializer
        return OrderStatusUpdateSerializer 
    def get_permissions(self): return [IsAuthenticated(), IsFrontDeskOrAdmin()] 

# --- Dispatch & Assignment API (Existing) ---
class OrderDispatchAssignmentView(APIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAdmin]
    def post(self, request, id):
        order = get_object_or_404(Order, id=id); assigned_delivery_id = request.data.get('assigned_delivery_id')
        if order.current_status != 'Ready for Dispatch': return Response({'detail': "Order must be 'Ready for Dispatch'."}, status=status.HTTP_400_BAD_REQUEST)
        if not assigned_delivery_id: return Response({'detail': 'assigned_delivery_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            delivery_personnel = User.objects.get(id=assigned_delivery_id)
            if delivery_personnel.role_key != UserRoles.DP: return Response({'detail': f"User {assigned_delivery_id} is not a Delivery Personnel."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist: return Response({'detail': 'Assigned user not found.'}, status=status.HTTP_400_BAD_REQUEST)
        order.assigned_delivery = delivery_personnel; order.current_status = 'Dispatched'; order.save()
        serializer = OrderSerializer(order)
        return Response({'detail': 'Order dispatched and assigned successfully.', 'order': serializer.data}, status=status.HTTP_200_OK)
        
# --- Delivery Personnel List View (Existing) ---
class DeliveryPersonnelListView(generics.ListAPIView):
    queryset = User.objects.filter(role_key=UserRoles.DP)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdmin | IsFrontDeskOrAdmin]
        
# --- GPS Tracking API (Compliance Check) (Existing) ---
class GPSTrackingView(generics.CreateAPIView):
    queryset = GPSTrackingHistory.objects.all()
    serializer_class = GPSTrackingSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        user = self.request.user; order_id = self.request.data.get('order')
        if not UserAttendance.objects.filter(user=user, clock_out_time__isnull=True).exists(): raise generics.exceptions.PermissionDenied("Tracking forbidden: User is not clocked in.")
        try: order = Order.objects.get(id=order_id)
        except Order.DoesNotExist: raise generics.exceptions.NotFound("Order not found.")
        if order.current_status != 'Dispatched': raise generics.exceptions.PermissionDenied(f"Tracking forbidden: Order status is {order.current_status}.")
        if order.assigned_delivery != user: raise generics.exceptions.PermissionDenied("Tracking forbidden: Order is not assigned to this user.")
        serializer.save(user=user, order=order)

# --- Proof of Execution API (QC/POD Upload) (Existing) ---
class ProofOfExecutionView(generics.CreateAPIView):
    queryset = ProofOfExecution.objects.all()
    serializer_class = ProofOfExecutionSerializer
    permission_classes = [IsAuthenticated] 
    def perform_create(self, serializer):
        user = self.request.user; proof_type = self.request.data.get('proof_type'); order_id = self.request.data.get('order')
        if proof_type == 'QC_Photo' and user.role_key not in [UserRoles.SP, UserRoles.LP]: raise generics.exceptions.PermissionDenied("QC Photo upload is restricted to Store/Lab Personnel.")
        if proof_type == 'POD_Photo' and user.role_key != UserRoles.DP: raise generics.exceptions.PermissionDenied("POD Photo upload is restricted to Delivery Personnel.")
        try: order = Order.objects.get(id=order_id)
        except Order.DoesNotExist: raise generics.exceptions.NotFound("Order not found.")
        if proof_type == 'QC_Photo' and order.current_status != 'Accepted/Preparing': raise generics.exceptions.PermissionDenied(f"QC Photo must be uploaded during 'Accepted/Preparing' status (current: {order.current_status}).")
        if proof_type == 'POD_Photo' and order.current_status != 'Dispatched': raise generics.exceptions.PermissionDenied(f"POD Photo must be uploaded when order is 'Dispatched' (current: {order.current_status}).")
        location_verified = (proof_type != 'POD_Photo')
        proof_instance = serializer.save(execution_user=user, order=order, is_location_verified=location_verified)
        if proof_type == 'QC_Photo': order.current_status = 'Ready for Dispatch'; order.save()
        elif proof_type == 'POD_Photo': order.current_status = 'Delivered'; order.save()
        return Response({'detail': 'Proof uploaded and delivery confirmed.', 'status': order.current_status}, status=status.HTTP_201_CREATED)

# --- Sales Planning API (List/Create/Update) (Existing) ---
class SalesVisitPlanCreateUpdateListView(generics.ListCreateAPIView):
    queryset = SalesVisitPlan.objects.all()
    serializer_class = SalesVisitPlanSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        if self.request.user.role_key != UserRoles.SR: raise generics.exceptions.PermissionDenied("Only Sales Representatives can create visit plans.")
        serializer.save(sales_rep=self.request.user)
    def get_queryset(self):
        user = self.request.user
        if user.role_key in [UserRoles.HLM, UserRoles.MLM]: return SalesVisitPlan.objects.all()
        return SalesVisitPlan.objects.filter(sales_rep=user)

class SalesVisitPlanRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SalesVisitPlan.objects.all()
    serializer_class = SalesVisitPlanSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if user.role_key in [UserRoles.HLM, UserRoles.MLM]: return SalesVisitPlan.objects.all()
        return SalesVisitPlan.objects.filter(sales_rep=user)

# --- Time Off Request API (Existing) ---
class TimeOffRequestView(generics.ListCreateAPIView):
    queryset = TimeOffRequest.objects.all()
    serializer_class = TimeOffRequestSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if user.role_key in [UserRoles.HLM, UserRoles.MLM, UserRoles.EM]: return TimeOffRequest.objects.all()
        return TimeOffRequest.objects.filter(user=user)
    def perform_create(self, serializer):
        user = self.request.user; manager = user.reporting_manager 
        if not manager: raise generics.exceptions.ValidationError({"detail": "Cannot submit request: You do not have an assigned reporting manager."})
        serializer.context['request'] = self.request 
        serializer.save(user=user, manager=manager)

# --- Time Off Approval API (Existing) ---
class TimeOffApprovalView(generics.UpdateAPIView):
    queryset = TimeOffRequest.objects.all()
    serializer_class = TimeOffApprovalSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated, IsPTOManager]
    def get_queryset(self):
        user = self.request.user
        return TimeOffRequest.objects.filter(manager=user, status='Request')
    def perform_update(self, serializer):
        request_instance = self.get_object(); new_status = self.request.data.get('status')
        with transaction.atomic():
            updated_request = serializer.save(approval_date=timezone.now())
            if updated_request.status == 'Approved':
                employee = updated_request.user; days_requested = updated_request.request_days
                if employee.pto_balance_days < days_requested: raise generics.exceptions.ValidationError({"detail": "Insufficient PTO balance for approval."})
                employee.pto_balance_days -= days_requested; employee.save()
            return updated_request

# --- Manager Status Override API (Existing) ---
class StaffStatusOverrideView(APIView):
    permission_classes = [IsAuthenticated, IsEmployeeManagerOrAdmin]
    def post(self, request):
        user_to_change_id = request.data.get('user_id'); new_status = request.data.get('new_status')
        status_reason = request.data.get('status_reason'); changing_manager = request.user
        if new_status != 'Unavailable': return Response({'detail': "Status can only be overridden to 'Unavailable'."}, status=status.HTTP_400_BAD_REQUEST)
        try: target_user = User.objects.get(id=user_to_change_id)
        except User.DoesNotExist: return Response({'detail': 'Target user not found.'}, status=status.HTTP_400_BAD_REQUEST)
        audit_serializer = StaffStatusAuditSerializer(data={'status_reason': status_reason})
        if not audit_serializer.is_valid(): return Response(audit_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try: attendance_record = UserAttendance.objects.get(user=target_user, clock_out_time__isnull=True)
        except UserAttendance.DoesNotExist: return Response({'detail': 'Target user is not currently clocked in.'}, status=status.HTTP_400_BAD_REQUEST)
        old_status = attendance_record.status
        with transaction.atomic():
            attendance_record.status = new_status; attendance_record.save()
            StaffStatusAudit.objects.create(user=target_user, changed_by=changing_manager, old_status=old_status, new_status=new_status, status_reason=status_reason)
        return Response({'detail': f"Status for {target_user.email} overridden to {new_status}.", 'audit_status': 'Logged'}, status=status.HTTP_200_OK)

# --- MLM Private Task API (Existing) ---
class MLMPrivateTaskListView(generics.ListCreateAPIView):
    queryset = MLMPrivateTask.objects.all()
    serializer_class = MLMPrivateTaskSerializer
    permission_classes = [IsAuthenticated, IsMLMOrHLM]
    def perform_create(self, serializer): serializer.save(mlm_user=self.request.user)
    def get_queryset(self):
        user = self.request.user
        if user.role_key == UserRoles.HLM: return MLMPrivateTask.objects.all()
        return MLMPrivateTask.objects.filter(mlm_user=user)

class MLMPrivateTaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MLMPrivateTask.objects.all()
    serializer_class = MLMPrivateTaskSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated, IsMLMOrHLM]
    def get_queryset(self):
        user = self.request.user
        if user.role_key == UserRoles.HLM: return MLMPrivateTask.objects.all()
        return MLMPrivateTask.objects.filter(mlm_user=user)

# --- KPI Dashboard API (Existing) ---
class KPIView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]

    def get(self, request):
        # 1. Average Cycle Time (from Order Creation to Delivery)
        cycle_time_data = Order.objects.filter(current_status='Delivered').annotate(
            cycle_duration=ExpressionWrapper(
                F('updated_at') - F('created_at'),
                output_field=fields.DurationField()
            )
        ).aggregate(
            avg_cycle_seconds=Avg('cycle_duration')
        )
        
        avg_cycle_minutes = (
            cycle_time_data.get('avg_cycle_seconds', timezone.timedelta(0)).total_seconds() / 60
            if cycle_time_data.get('avg_cycle_seconds') else 0
        )
        
        # 2. Protocol Adherence % (Compliance: QC Photo completion for Store Orders)
        total_store_orders = Order.objects.filter(processing_type='Store').count()
        
        compliant_store_orders = Order.objects.filter(
            processing_type='Store',
            proofs__proof_type='QC_Photo'
        ).distinct().count()
        
        protocol_adherence_percent = (
            (compliant_store_orders / total_store_orders) * 100
            if total_store_orders > 0 else 0
        )

        # 3. Sales Planning Adherence Rate (Visits vs. Planned)
        total_planned_visits = SalesVisitPlan.objects.all().count()
        total_missed_visits = SalesVisitPlan.objects.filter(status='Missed').count()
        
        adherence_rate = (
            ((total_planned_visits - total_missed_visits) / total_planned_visits) * 100
            if total_planned_visits > 0 else 0
        )

        kpi_data = {
            "average_cycle_time_minutes": round(avg_cycle_minutes, 2),
            "protocol_adherence_percent": round(protocol_adherence_percent, 2),
            "sales_planning_adherence_rate": round(adherence_rate, 2),
        }
        
        return Response(kpi_data)
        
# -------------------------------------------------------------------
# NEW: Audit Log APIs (Phase IV, Step 17)
# -------------------------------------------------------------------

class StaffStatusAuditListView(generics.ListAPIView):
    """
    Exposes the detailed log of all staff status changes (override compliance).
    Only visible to Managers (HLM, MLM).
    """
    queryset = StaffStatusAudit.objects.select_related('user', 'changed_by').all()
    serializer_class = StaffStatusAuditListSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdmin] # HLM/MLM oversight

class GPSTrackingHistoryListView(generics.ListAPIView):
    """
    Exposes the full history of GPS coordinates for audit and map visualization.
    Only visible to Managers (HLM, MLM).
    """
    queryset = GPSTrackingHistory.objects.select_related('user', 'order').all()
    serializer_class = GPSTrackingSerializer # Re-uses the existing tracking serializer
    permission_classes = [IsAuthenticated, IsManagerOrAdmin] # HLM/MLM oversight