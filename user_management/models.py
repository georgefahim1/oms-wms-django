# user_management/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

# ---------------------------------------------------------
# A. CUSTOM USER MANAGER 
# ---------------------------------------------------------
class CustomUserManager(BaseUserManager):
    # ... (Existing methods for create_user and create_superuser remain here)
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
# B. USER MODEL ROLES AND DEFINITION (Existing code)
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
# C. NEW: User_Attendance Model
# ---------------------------------------------------------

class UserAttendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    
    # Times
    clock_in_time = models.DateTimeField(auto_now_add=True) # Set on creation
    clock_out_time = models.DateTimeField(null=True, blank=True)
    
    # Status (Used for future audit; currently simplified to reflect clock state)
    status = models.CharField(max_length=20, default='Available')
    
    # Calculation (Duration Minutes)
    duration_minutes = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.clock_in_time.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        # Calculate duration if clock_out_time is set
        if self.clock_in_time and self.clock_out_time and self.duration_minutes is None:
            duration = self.clock_out_time - self.clock_in_time
            self.duration_minutes = int(duration.total_seconds() / 60)
            
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'User Attendance'
        verbose_name_plural = 'User Attendance'
        ordering = ['-clock_in_time'] # Latest entry first