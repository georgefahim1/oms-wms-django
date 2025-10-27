# user_management/views.py

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User
from .serializers import UserSerializer
from .permissions import IsManagerOrAdmin 

# --- Register API (Protected) ---
class UserCreateView(generics.CreateAPIView):
    """
    API endpoint for creating new system users.
    Only accessible by High-Level and Middle-Level Managers.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Apply permissions: Requires authentication AND the user must be a Manager
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]