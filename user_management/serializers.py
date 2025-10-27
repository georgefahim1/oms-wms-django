# user_management/serializers.py

from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Fields required for registering a new user
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'role_key', 'reporting_manager')
        # Extra fields configuration for security (password write-only)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Use Django's built-in create_user for password hashing
        user = User.objects.create_user(**validated_data)
        return user