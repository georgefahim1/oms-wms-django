# user_management/serializers.py

from rest_framework import serializers
from django.db import transaction
from .models import User, UserAttendance, Order, OrderItem 

# --- Existing Serializers ---

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'role_key', 'reporting_manager')
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
        
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

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=True) 

    class Meta:
        model = Order
        fields = (
            'id', 'client_name', 'shipping_address', 'processing_type', 
            'destination_latitude', 'destination_longitude', 'items', 'order_creator'
        )
        read_only_fields = ('order_creator',) 

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for item_data in items_data:
                OrderItem.objects.create(order=order, **item_data)
            return order

# --- NEW: Status Update Serializer ---
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        # Only allow current_status to be updated
        fields = ('id', 'processing_type', 'current_status')
        read_only_fields = ('id', 'processing_type') # These fields are for reading only during update

    def validate_current_status(self, value):
        # Enforce business logic: Status must move forward sequentially
        # NOTE: This check is often complex; here we simply ensure it's a valid choice.
        # More complex checks (e.g., must go from Pending -> Accepted) would be added here.
        
        # Check if the new status is valid according to model choices
        if value not in [choice[0] for choice in Order.STATUS_CHOICES]:
             raise serializers.ValidationError(f"'{value}' is not a valid status.")
             
        # In a real system, more complex checks go here:
        # Example: if self.instance and value == 'Delivered' and self.instance.current_status != 'Dispatched':
        #             raise serializers.ValidationError("Cannot deliver an order that hasn't been dispatched.")

        return value