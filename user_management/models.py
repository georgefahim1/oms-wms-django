# user_management/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
import uuid 

# ---------------------------------------------------------
# A. CUSTOM USER MANAGER (Existing code)
# ---------------------------------------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email: raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True); extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True); extra_fields.setdefault('role_key', UserRoles.HLM)
        if extra_fields.get('is_staff') is not True: raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True: raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

# ---------------------------------------------------------
# B. USER MODEL ROLES AND DEFINITION (Existing code)
# ---------------------------------------------------------
class UserRoles(models.TextChoices):
    HLM = 'High-Level Manager', 'High-Level Manager'; MLM = 'Middle-Level Manager', 'Middle-Level Manager'
    EM = 'Employee Manager', 'Employee Manager'; SR = 'Sales Rep', 'Sales Rep'
    FD = 'Front Desk', 'Front Desk'; SP = 'Store Personnel', 'Store Personnel'
    LP = 'Lab Personnel', 'Lab Personnel'; DP = 'Delivery Personnel', 'Delivery Personnel'

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=False, null=True, blank=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    role_key = models.CharField(max_length=50, choices=UserRoles.choices, default=UserRoles.SR, verbose_name='System Role')
    reporting_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='reportees', verbose_name='Reporting Manager')
    pto_balance_days = models.DecimalField(max_digits=4, decimal_places=1, default=10.0)
    USERNAME_FIELD = 'email'; REQUIRED_FIELDS = ['first_name', 'last_name', 'role_key']; objects = CustomUserManager()
    def __str__(self): return f"{self.first_name} {self.last_name} ({self.role_key})"
    class Meta:
        verbose_name = 'System User'; verbose_name_plural = 'System Users'

# ---------------------------------------------------------
# C. User_Attendance Model (Existing code)
# ---------------------------------------------------------
class UserAttendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    clock_in_time = models.DateTimeField(auto_now_add=True); clock_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Available'); duration_minutes = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.user.email} - {self.clock_in_time.strftime('%Y-%m-%d')}"
    def save(self, *args, **kwargs):
        if self.clock_in_time and self.clock_out_time and self.duration_minutes is None:
            duration = self.clock_out_time - self.clock_in_time
            self.duration_minutes = int(duration.total_seconds() / 60)
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = 'User Attendance'; verbose_name_plural = 'User Attendance'; ordering = ['-clock_in_time']

# ---------------------------------------------------------
# D. Order and OrderItem Models (Existing code)
# ---------------------------------------------------------
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_name = models.CharField(max_length=100); shipping_address = models.TextField()
    destination_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    destination_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'), ('Accepted/Preparing', 'Accepted/Preparing'),
        ('Ready for Dispatch', 'Ready for Dispatch'), ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'),
    ]
    PROCESSING_CHOICES = [('Lab', 'Lab'), ('Store', 'Store'), ('DirectDispatch', 'Direct Dispatch'),]
    current_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    processing_type = models.CharField(max_length=20, choices=PROCESSING_CHOICES)
    order_creator = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='created_orders')
    assigned_delivery = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_deliveries', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"Order {self.id} for {self.client_name} - {self.current_status}"
    class Meta:
        verbose_name = 'Client Order'; verbose_name_plural = 'Client Orders'; ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    sku_code = models.CharField(max_length=50); quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.quantity} x {self.sku_code} on Order {self.order_id}"
    class Meta:
        verbose_name = 'Order Item'; verbose_name_plural = 'Order Items'; unique_together = ('order', 'sku_code') 
        
# ---------------------------------------------------------
# E. GPS_Tracking_History Model (Existing code)
# ---------------------------------------------------------
class GPSTrackingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gps_tracks')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='gps_tracks')
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    recorded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Track: {self.user.email} @ {self.recorded_at.isoformat()}"
    class Meta:
        verbose_name = 'GPS Tracking History'; verbose_name_plural = 'GPS Tracking History'; ordering = ['-recorded_at']
        
# ---------------------------------------------------------
# F. ProofOfExecution Model (Existing code)
# ---------------------------------------------------------
class ProofOfExecution(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='proofs')
    execution_user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='proofs_provided')
    PROOF_CHOICES = [
        ('QC_Photo', 'Quality Control Photo'),
        ('POD_Photo', 'Proof of Delivery Photo'),
    ]
    proof_type = models.CharField(max_length=20, choices=PROOF_CHOICES)
    qc_pod_photo = models.FileField(upload_to='proof_uploads/') 
    gps_latitude = models.DecimalField(max_digits=10, decimal_places=8)
    gps_longitude = models.DecimalField(max_digits=11, decimal_places=8)
    is_location_verified = models.BooleanField(default=False)
    executed_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.proof_type} for Order {self.order_id}"
    class Meta:
        verbose_name = 'Proof of Execution'; verbose_name_plural = 'Proof of Execution'; ordering = ['-executed_at']

# ---------------------------------------------------------
# G. NEW: SalesVisitPlan Model
# ---------------------------------------------------------
class SalesVisitPlan(models.Model):
    sales_rep = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visit_plans')
    client_name = models.CharField(max_length=100)
    visit_date = models.DateField()
    
    STATUS_CHOICES = [
        ('Planned', 'Planned'),
        ('Visited', 'Visited'),
        ('Missed', 'Missed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Planned')
    visit_notes = models.TextField(null=True, blank=True)
    missed_remark = models.TextField(null=True, blank=True) # CRITICAL: Mandatory when status is 'Missed'
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Plan for {self.client_name} by {self.sales_rep.last_name} on {self.visit_date}"

    class Meta:
        verbose_name = 'Sales Visit Plan'
        verbose_name_plural = 'Sales Visit Plans'
        ordering = ['visit_date']