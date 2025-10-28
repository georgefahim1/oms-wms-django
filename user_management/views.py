# user_management/views.py

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import User, UserAttendance, Order, UserRoles, GPSTrackingHistory, ProofOfExecution, SalesVisitPlan, TimeOffRequest, StaffStatusAudit # Import new model
from .serializers import (
    UserSerializer, UserAttendanceSerializer, OrderSerializer,
    OrderStatusUpdateSerializer, GPSTrackingSerializer, CustomTokenObtainPairSerializer, 
    ProofOfExecutionSerializer, SalesVisitPlanSerializer,
    TimeOffRequestSerializer, TimeOffApprovalSerializer,
    StaffStatusAuditSerializer # Import new serializer
)
from .permissions import IsManagerOrAdmin, IsFrontDeskOrAdmin, IsEmployeeManagerOrAdmin # Import new permission

# -------------------------------------------------------------------
# NEW: PTO Management Permissions (Existing, moved up for visibility)
# -------------------------------------------------------------------
class IsManager(IsAuthenticated):
    """Allows access only to HLM, MLM, and Employee Managers."""
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return request.user.role_key in [UserRoles.HLM, UserRoles.MLM, UserRoles.EM]
        return False

# -------------------------------------------------------------------
# VIEWS (Existing Code)
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
        if user.role_key in ['High-Level Manager', 'Middle-Level Manager', 'Front Desk']: return Order.objects.all()
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
        if order.current_status != 'Ready for Dispatch': return Response({'detail': f"Order must be 'Ready for Dispatch' (current status: {order.current_status})."}, status=status.HTTP_400_BAD_REQUEST)
        if not assigned_delivery_id: return Response({'detail': 'assigned_delivery_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            delivery_personnel = User.objects.get(id=assigned_delivery_id)
            if delivery_personnel.role_key != UserRoles.DP: return Response({'detail': f"User {assigned_delivery_id} is not a Delivery Personnel. Role is {delivery_personnel.role_key}."}, status=status.HTTP_400_BAD_REQUEST)
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
    permission_classes = [IsManager]
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

# -------------------------------------------------------------------
# NEW: Manager Status Override API (Step 13)
# -------------------------------------------------------------------
class StaffStatusOverrideView(APIView):
    permission_classes = [IsAuthenticated, IsEmployeeManagerOrAdmin]

    def post(self, request):
        """
        Allows managers to change a low-level employee's status to 'Unavailable' 
        and logs the mandatory reason.
        """
        user_to_change_id = request.data.get('user_id')
        new_status = request.data.get('new_status')
        status_reason = request.data.get('status_reason')
        changing_manager = request.user

        if new_status != 'Unavailable':
            return Response({'detail': "Status can only be overridden to 'Unavailable'."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Look up the target user
        try:
            target_user = User.objects.get(id=user_to_change_id)
        except User.DoesNotExist:
            return Response({'detail': 'Target user not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Validation: Ensure compliance for mandatory reason
        data = {'status_reason': status_reason}
        audit_serializer = StaffStatusAuditSerializer(data=data)

        # The serializer's validate_status_reason handles the compliance check
        if not audit_serializer.is_valid():
            # Returns 400 if status_reason is missing
            return Response(audit_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 3. CRITICAL: Find the current open attendance record
        try:
            attendance_record = UserAttendance.objects.get(user=target_user, clock_out_time__isnull=True)
        except UserAttendance.DoesNotExist:
            return Response({'detail': 'Target user is not currently clocked in.'}, status=status.HTTP_400_BAD_REQUEST)

        old_status = attendance_record.status # Capture the status before change

        with transaction.atomic():
            # 4. Update the Attendance Record Status
            attendance_record.status = new_status
            attendance_record.save()

            # 5. Create the Mandatory Audit Trail Record
            StaffStatusAudit.objects.create(
                user=target_user,
                changed_by=changing_manager,
                old_status=old_status,
                new_status=new_status,
                status_reason=status_reason
            )

        return Response({
            'detail': f"Status for {target_user.email} overridden to {new_status}.",
            'audit_status': 'Logged'
        }, status=status.HTTP_200_OK)