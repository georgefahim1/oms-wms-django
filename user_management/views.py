# user_management/views.py

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
    
from .models import User, UserAttendance
from .serializers import UserSerializer, UserAttendanceSerializer # <-- NOW CORRECTLY IMPORTED
from .permissions import IsManagerOrAdmin 

# --- Register API (Protected) ---
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdmin] 
    
# --- Attendance API (Clock In/Out) ---
class AttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Endpoint to handle Clock In."""
        user = request.user
        
        # Check if user is already clocked in
        if UserAttendance.objects.filter(user=user, clock_out_time__isnull=True).exists():
            return Response({'detail': 'User is already clocked in.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Create a new attendance record (Clock In)
        # We don't need 'data' in the call since clock_in_time is auto_now_add=True
        serializer = UserAttendanceSerializer(data={}) 
        if serializer.is_valid():
            serializer.save(user=user, status='Available')
            return Response({'detail': 'Clocked in successfully.', 'record': serializer.data}, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Endpoint to handle Clock Out."""
        user = request.user
        
        # Find the most recent, open attendance record
        try:
            open_record = UserAttendance.objects.get(user=user, clock_out_time__isnull=True)
        except UserAttendance.DoesNotExist:
            return Response({'detail': 'No active clock-in found.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Update the clock_out_time and status
        open_record.clock_out_time = timezone.now()
        open_record.status = 'Unavailable' # Update status on clock-out
        
        # The save method in the model will calculate duration_minutes
        open_record.save() 
        
        serializer = UserAttendanceSerializer(open_record)
        return Response({'detail': 'Clocked out successfully.', 'record': serializer.data}, status=status.HTTP_200_OK)

    def get(self, request):
        """Returns the current clock-in status for the user."""
        user = request.user
        is_clocked_in = UserAttendance.objects.filter(user=user, clock_out_time__isnull=True).exists()
        
        return Response({'is_clocked_in': is_clocked_in, 'user_id': user.id}, status=status.HTTP_200_OK)