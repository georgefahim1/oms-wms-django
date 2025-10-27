# user_management/serializers.py

from rest_framework import serializers
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    User, UserAttendance, Order, OrderItem, GPSTrackingHistory, 
    ProofOfExecution # Import new model
)

# --- Existing Serializers ---
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'id': self.user.id, 'email': self.user.email,
            'first_name': self.user.first_name, 'role': self.user.role_key,
        })
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'role_key', 'reporting_manager')
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data); return user

class UserAttendanceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True) 
    class Meta:
        model = UserAttendance
        fields = ('id', 'user', 'clock_in_time', 'clock_out_time', 'status', 'duration_minutes')
        read_only_fields = ('clock_in_time', 'duration_minutes', 'status')

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'sku_code', 'quantity', 'unit_price')

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'processing_type', 'current_status')
        read_only_fields = ('id', 'processing_type')
    def validate_current_status(self, value):
        if value not in [choice[0] for choice in Order.STATUS_CHOICES]:
             raise serializers.ValidationError(f"'{value}' is not a valid status.")
        return value

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=True) 
    class Meta:
        model = Order
        fields = ('id', 'client_name', 'shipping_address', 'processing_type', 'destination_latitude', 'destination_longitude', 'items', 'order_creator')
        read_only_fields = ('order_creator',) 
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for item_data in items_data:
                OrderItem.objects.create(order=order, **item_data)
            return order

class GPSTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPSTrackingHistory
        fields = ('id', 'order', 'latitude', 'longitude', 'recorded_at')
        read_only_fields = ('recorded_at',)

# --- NEW: Proof of Execution Serializer ---
class ProofOfExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProofOfExecution
        fields = (
            'id', 'order', 'proof_type', 'qc_pod_photo', 
            'gps_latitude', 'gps_longitude', 'executed_at'
        )
        read_only_fields = ('executed_at',)