# user_management/views.py

from rest_framework import generics, status, exceptions # <-- FIX: Import exceptions here
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
    
from .models import User, UserAttendance, Order, UserRoles, GPSTrackingHistory 
from .serializers import (
    UserSerializer, UserAttendanceSerializer, OrderSerializer,
    OrderStatusUpdateSerializer, GPSTrackingSerializer, CustomTokenObtainPairSerializer 
)
from .permissions import IsManagerOrAdmin, IsFrontDeskOrAdmin 

# -------------------------------------------------------------------
# FIX: Custom Login View (Recursion Fix Implementation)
# -------------------------------------------------------------------
class CustomTokenObtainPairView(TokenObtainPairView):
    """Overrides the default JWT view to use our custom serializer."""
    serializer_class = CustomTokenObtainPairSerializer

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
        if UserAttendance.objects.filter(user=user, clock_out_time__isnull=True).exists():
            return Response({'detail': 'User is already clocked in.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserAttendanceSerializer(data={'user': user.id})
        if serializer.is_valid():
            serializer.save(user=user, status='Available')
            return Response({'detail': 'Clocked in successfully.', 'record': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user = request.user
        try:
            open_record = UserAttendance.objects.get(user=user, clock_out_time__isnull=True)
        except UserAttendance.DoesNotExist:
            return Response({'detail': 'No active clock-in found.'}, status=status.HTTP_400_BAD_REQUEST)
        open_record.clock_out_time = timezone.now()
        open_record.save() 
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

    def perform_create(self, serializer):
        serializer.save(order_creator=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.role_key in ['High-Level Manager', 'Middle-Level Manager', 'Front Desk']:
             return Order.objects.all()
        return Order.objects.filter(order_creator=user)

# --- Order Routing & Status Update API (Existing) ---
class OrderRetrieveUpdateStatusView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderSerializer
        return OrderStatusUpdateSerializer 

    def get_permissions(self):
        return [IsAuthenticated(), IsFrontDeskOrAdmin()] 

# --- Dispatch & Assignment API (Existing) ---
class OrderDispatchAssignmentView(APIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAdmin]

    def post(self, request, id):
        order = get_object_or_404(Order, id=id)
        assigned_delivery_id = request.data.get('assigned_delivery_id')

        if order.current_status != 'Ready for Dispatch':
            return Response({'detail': f"Order must be 'Ready for Dispatch' (current status: {order.current_status})."}, status=status.HTTP_400_BAD_REQUEST)

        if not assigned_delivery_id:
            return Response({'detail': 'assigned_delivery_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            delivery_personnel = User.objects.get(id=assigned_delivery_id)
            if delivery_personnel.role_key != UserRoles.DP:
                return Response({'detail': f"User {assigned_delivery_id} is not a Delivery Personnel. Role is {delivery_personnel.role_key}."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'detail': 'Assigned user not found.'}, status=status.HTTP_400_BAD_REQUEST)

        order.assigned_delivery = delivery_personnel
        order.current_status = 'Dispatched'
        order.save()

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
        user = self.request.user
        order_id = self.request.data.get('order')
        
        # 1. CRITICAL COMPLIANCE CHECK: Is the user Clocked In?
        if not UserAttendance.objects.filter(user=user, clock_out_time__isnull=True).exists():
            # FIX: Use exceptions.PermissionDenied instead of generics.exceptions.PermissionDenied
            raise exceptions.PermissionDenied("Tracking forbidden: User is not clocked in.") 

        # 2. CRITICAL COMPLIANCE CHECK: Is the Order Dispatched AND assigned to this user?
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            # FIX: Use exceptions.NotFound instead of generics.exceptions.NotFound
            raise exceptions.NotFound("Order not found.") 

        if order.current_status != 'Dispatched':
            raise exceptions.PermissionDenied(f"Tracking forbidden: Order status is {order.current_status}.")

        if order.assigned_delivery != user:
            raise exceptions.PermissionDenied("Tracking forbidden: Order is not assigned to this user.")

        # 3. Save the tracking data if all checks pass
        serializer.save(user=user, order=order)