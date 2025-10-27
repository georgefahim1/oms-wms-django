# user_management/views.py

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
    
from .models import User, UserAttendance, Order
from .serializers import (
    UserSerializer, UserAttendanceSerializer, OrderSerializer,
    OrderStatusUpdateSerializer # Import new serializer
)
from .permissions import IsManagerOrAdmin, IsFrontDeskOrAdmin # Import new permission

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

# --- NEW: Order Routing & Status Update API ---
class OrderRetrieveUpdateStatusView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    lookup_field = 'id' # Use the UUID field for lookup

    def get_serializer_class(self):
        # Use the full serializer for GET requests (retrieve data)
        if self.request.method == 'GET':
            return OrderSerializer
        # Use the restricted serializer for PUT/PATCH requests (status update)
        return OrderStatusUpdateSerializer 

    def get_permissions(self):
        # Only Front Desk can initially route and change status
        # This will be extended in later steps for Store/Lab personnel
        return [IsAuthenticated(), IsFrontDeskOrAdmin()]