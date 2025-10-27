# user_management/views.py

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone

from .models import User, UserAttendance, Order # Import new model
from .serializers import (
    UserSerializer, UserAttendanceSerializer, OrderSerializer # Import new serializer
)
from .permissions import IsManagerOrAdmin 

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

# --- NEW: Order Creation API ---
class OrderCreateListView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated] # Only authenticated users can create orders

    def perform_create(self, serializer):
        # CRITICAL: Ensures the order_creator is automatically set to the logged-in user
        # regardless of client input.
        serializer.save(order_creator=self.request.user)

    def get_queryset(self):
        # Restricts the list view to only show orders created by the user, 
        # unless the user is a manager (HLM/MLM/Front Desk) who needs broader access.
        user = self.request.user
        if user.role_key in ['High-Level Manager', 'Middle-Level Manager', 'Front Desk']:
             return Order.objects.all()

        # Default: Show only orders created by the current user (e.g., Sales Reps)
        return Order.objects.filter(order_creator=user)