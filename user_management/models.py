# user_management/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
import uuid # For UUID primary keys

# ---------------------------------------------------------
# A. CUSTOM USER MANAGER 
# ---------------------------------------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role_key', UserRoles.HLM)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)

# ---------------------------------------------------------
# B. USER MODEL ROLES AND DEFINITION
# ---------------------------------------------------------
class UserRoles(models.TextChoices):
    HLM = 'High-Level Manager', 'High-Level Manager'
    MLM = 'Middle-Level Manager', 'Middle-Level Manager'
    EM = 'Employee Manager', 'Employee Manager'
    SR = 'Sales Rep', 'Sales Rep'
    FD = 'Front Desk', 'Front Desk'
    SP = 'Store Personnel', 'Store Personnel'
    LP = 'Lab Personnel', 'Lab Personnel'
    DP = 'Delivery Personnel', 'Delivery Personnel'

class User(AbstractUser):
    # Core Fields
    username = models.CharField(max_length=150, unique=False, null=True, blank=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    role_key = models.CharField(
        max_length=50,
        choices=UserRoles.choices,
        default=UserRoles.SR,
        verbose_name='System Role'
    )
    # Reporting Structure
    reporting_manager = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportees',
        verbose_name='Reporting Manager'
    )
    # Additional Fields
    pto_balance_days = models.DecimalField(max_digits=4, decimal_places=1, default=10.0)

    # Configuration
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role_key']
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role_key})"

    class Meta:
        verbose_name = 'System User'
        verbose_name_plural = 'System Users'

# ---------------------------------------------------------
# C. User_Attendance Model (Existing code)
# ---------------------------------------------------------
class UserAttendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    clock_in_time = models.DateTimeField(auto_now_add=True)
    clock_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Available')
    duration_minutes = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.clock_in_time.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        if self.clock_in_time and self.clock_out_time and self.duration_minutes is None:
            duration = self.clock_out_time - self.clock_in_time
            self.duration_minutes = int(duration.total_seconds() / 60)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'User Attendance'
        verbose_name_plural = 'User Attendance'
        ordering = ['-clock_in_time']

# ---------------------------------------------------------
# D. NEW: Order and OrderItem Models
# ---------------------------------------------------------

class Order(models.Model):
    # Order Tracking
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Use UUIDs for unique ID
    
    # Client and Location Info
    client_name = models.CharField(max_length=100)
    shipping_address = models.TextField()
    destination_latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    destination_longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Workflow Status
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted/Preparing', 'Accepted/Preparing'),
        ('Ready for Dispatch', 'Ready for Dispatch'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    PROCESSING_CHOICES = [
        ('Lab', 'Lab'),
        ('Store', 'Store'),
        ('DirectDispatch', 'Direct Dispatch'),
    ]

    current_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    processing_type = models.CharField(max_length=20, choices=PROCESSING_CHOICES) # CRITICAL: For Routing (Phase II, Step 6)
    
    # Personnel
    order_creator = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='created_orders') # Sales Rep / Front Desk
    assigned_delivery = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_deliveries', null=True, blank=True) # Delivery Personnel
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} for {self.client_name} - {self.current_status}"

    class Meta:
        verbose_name = 'Client Order'
        verbose_name_plural = 'Client Orders'
        ordering = ['-created_at']

class OrderItem(models.Model):
    # Relationship
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items') # Deleting an order deletes all items
    
    # Product Details
    sku_code = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.sku_code} on Order {self.order_id}"

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        # Ensures that a single SKU is only listed once per order (if business logic requires unique items)
        unique_together = ('order', 'sku_code')