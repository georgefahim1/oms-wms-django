# user_management/serializers.py

from rest_framework import serializers
from django.db import transaction
from .models import User, UserAttendance, Order, OrderItem # Import new models

# --- User and Attendance (Existing) ---
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

# --- NEW: Nested OrderItem Serializer ---
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'sku_code', 'quantity', 'unit_price')

# --- NEW: Order Serializer with Nested Items (CREATE) ---
class OrderSerializer(serializers.ModelSerializer):
    # Define the nested relationship for order items (multi-line input)
    items = OrderItemSerializer(many=True, required=True) 

    class Meta:
        model = Order
        fields = (
            'id', 'client_name', 'shipping_address', 'processing_type', 
            'destination_latitude', 'destination_longitude', 'items', 'order_creator'
        )
        read_only_fields = ('order_creator',) # Handled automatically by the view

    def create(self, validated_data):
        # 1. Extract the nested items data
        items_data = validated_data.pop('items')

        # 2. Use a transaction to ensure either the Order AND all Items are saved, or none are.
        with transaction.atomic():
            # 3. Create the parent Order object
            order = Order.objects.create(**validated_data)

            # 4. Create all nested OrderItem objects
            for item_data in items_data:
                OrderItem.objects.create(order=order, **item_data)

            return order