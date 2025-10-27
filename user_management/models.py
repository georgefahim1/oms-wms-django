# user_management/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


# ---------------------------------------------------------
# A. CUSTOM USER MANAGER (FIXES THE USERNAME ERROR)
# ---------------------------------------------------------
class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        # We ensure that required admin fields are set
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role_key', UserRoles.HLM) # Force superuser role

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        # FIX: We now call create_user directly, bypassing the default AbstractUser manager
        # The 'username' field is left as None/Blank, as per our model definition.
        return self.create_user(email, password, **extra_fields)


# ---------------------------------------------------------
# B. USER MODEL DEFINITION
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
    # We will use email for login
    username = models.CharField(max_length=150, unique=False, null=True, blank=True)
    email = models.EmailField(unique=True, blank=False, null=False) # CRITICAL: Email as unique identifier

    role_key = models.CharField(
        max_length=50,
        choices=UserRoles.choices,
        default=UserRoles.SR,
        verbose_name='System Role'
    )

    reporting_manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportees',
        verbose_name='Reporting Manager'
    )
    
    pto_balance_days = models.DecimalField(max_digits=4, decimal_places=1, default=10.0)

    # Required field configuration
    USERNAME_FIELD = 'email' # Tell Django to use email for login
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role_key'] # Fields prompted in createsuperuser

    # Tell the User model to use our CustomUserManager
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role_key})"

    class Meta:
        verbose_name = 'System User'
        verbose_name_plural = 'System Users'