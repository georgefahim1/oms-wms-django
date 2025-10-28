# user_management/serializers.py

from rest_framework import serializers
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    User, UserAttendance, Order, OrderItem, GPSTrackingHistory, 
    ProofOfExecution, SalesVisitPlan, TimeOffRequest, StaffStatusAudit,
    MLMPrivateTask # Import new model
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
        if value not in [choice[0] for choice in Order.STATUS_CHOICES]: raise serializers.ValidationError(f"'{value}' is not a valid status.")
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
            for item_data in items_data: OrderItem.objects.create(order=order, **item_data)
            return order

class GPSTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPSTrackingHistory
        fields = ('id', 'order', 'latitude', 'longitude', 'recorded_at')
        read_only_fields = ('recorded_at',)

class ProofOfExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProofOfExecution
        fields = ('id', 'order', 'proof_type', 'qc_pod_photo', 'gps_latitude', 'gps_longitude', 'executed_at')
        read_only_fields = ('executed_at',)

class SalesVisitPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesVisitPlan
        fields = ('id', 'client_name', 'visit_date', 'status', 'visit_notes', 'missed_remark', 'sales_rep')
        read_only_fields = ('sales_rep',)
    def validate(self, data):
        status_value = data.get('status', self.instance.status if self.instance else 'Planned')
        missed_remark = data.get('missed_remark')
        if status_value == 'Missed' and not missed_remark:
            raise serializers.ValidationError({"missed_remark": "Compliance required: A mandatory remark must be added for all missed visits."})
        return data

class TimeOffRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeOffRequest
        fields = ('id', 'user', 'manager', 'start_date', 'end_date', 'request_days', 'reason', 'status', 'created_at')
        read_only_fields = ('user', 'status', 'manager') 
    def validate(self, data):
        if data['start_date'] > data['end_date']: raise serializers.ValidationError("Start date cannot be after the end date.")
        if data['request_days'] <= 0: raise serializers.ValidationError("Request days must be greater than zero.")
        if self.instance is None:
            user = self.context['request'].user
            if data['request_days'] > user.pto_balance_days: raise serializers.ValidationError(f"Insufficient PTO balance. Available: {user.pto_balance_days} days.")
        return data

class TimeOffApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeOffRequest
        fields = ('id', 'status')
        read_only_fields = ('id',)
    def validate_status(self, value):
        if value not in ['Approved', 'Rejected']: raise serializers.ValidationError("Status can only be set to 'Approved' or 'Rejected'.")
        if self.instance and self.instance.status != 'Request': raise serializers.ValidationError(f"Cannot change status from {self.instance.status}.")
        return value

class StaffStatusAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffStatusAudit
        fields = ('id', 'user', 'old_status', 'new_status', 'status_reason', 'changed_by', 'change_time')
        read_only_fields = ('user', 'old_status', 'new_status', 'changed_by', 'change_time')
    def validate_status_reason(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Compliance required: A mandatory reason must be logged for the status change.")
        return value

# --- NEW: MLM Private Task Serializer ---
class MLMPrivateTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLMPrivateTask
        fields = ('id', 'title', 'description', 'time_logged_minutes', 'completed', 'created_at', 'mlm_user')
        read_only_fields = ('mlm_user',) # Task owner is set by the API