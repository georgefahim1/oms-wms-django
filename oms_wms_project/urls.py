# oms_wms_project/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

# IMPORT THE CUSTOM SERIALIZER HERE (It won't cause recursion here)
from user_management.serializers import CustomTokenObtainPairSerializer 
from rest_framework_simplejwt.views import TokenObtainPairView 


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- Authentication APIs (Login/Token) ---
    # Use the base view but apply the custom serializer for user data in the response
    path('api/token/', TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer), name='token_obtain_pair'), 
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints for our custom apps
    path('api/', include('user_management.urls')),
]

# --- Media File Serving (REQUIRED for development) ---
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)