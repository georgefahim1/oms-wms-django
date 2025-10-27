# user_management/serializers.py

from rest_framework import serializers
from .models import User, UserAttendance # Import the new UserAttendance model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'role_key', 'reporting_manager')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
        
class UserAttendanceSerializer(serializers.ModelSerializer):
    # Only need to read user ID for response; user is set automatically in the view
    user = serializers.PrimaryKeyRelatedField(read_only=True) 

    class Meta:
        model = UserAttendance
        fields = ('id', 'user', 'clock_in_time', 'clock_out_time', 'status', 'duration_minutes')
        read_only_fields = ('clock_in_time', 'duration_minutes', 'status') # User cannot set these