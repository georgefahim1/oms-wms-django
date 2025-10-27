# oms_wms_project/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from django.conf import settings # <-- REQUIRED: For accessing settings.DEBUG and MEDIA_URL
from django.conf.urls.static import static # <-- REQUIRED: For serving media files

# Imports for custom views
from user_management.serializers import CustomTokenObtainPairSerializer 
from rest_framework_simplejwt.views import TokenObtainPairView 


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication APIs (Login/Token) 
    path('api/token/', TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer), name='token_obtain_pair'), 
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints for our custom apps
    path('api/', include('user_management.urls')),
]

# --- Media File Serving (REQUIRED for development/debug) ---
# This serves files uploaded to the 'media' folder when Django is running in DEBUG mode.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)