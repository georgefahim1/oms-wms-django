"""
URL configuration for oms_wms_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# oms_wms_project/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- Authentication APIs (Login/Token) ---
    # POST /api/token/ -> Returns access (JWT) and refresh token
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 

    # POST /api/token/refresh/ -> Refreshes an expired access token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API endpoints for our custom apps
    path('api/', include('user_management.urls')), # <-- Add app URLs here
]