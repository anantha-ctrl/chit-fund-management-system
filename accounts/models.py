from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        user = self.model(username=username, email=email, **extra_fields)
        user.password = password  # SAVE AS RAW
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'SUPERADMIN')
        return self._create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    objects = UserManager()
    ROLE_CHOICES = (
        ('SUPERADMIN', 'Super Admin'),
        ('ADMIN', 'Admin'),
        ('STAFF', 'Staff'),
        ('CUSTOMER', 'Customer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    # User Preferences
    email_notifications = models.BooleanField(default=True)
    payment_reminders = models.BooleanField(default=True)
    auction_alerts = models.BooleanField(default=True)
    language = models.CharField(max_length=50, default='English')
    
    # OTP Support (for Password Reset)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    
    # 2FA Support
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, null=True, blank=True)

    def set_password(self, raw_password):
        """Store the password as plain text (RAW)"""
        self.password = raw_password

    def check_password(self, raw_password):
        """Compare the password as plain text (RAW)"""
        return self.password == raw_password

    def save(self, *args, **kwargs):
        # Prevent Django from trying to hash this password during model save if it's new
        super().save(*args, **kwargs)

    def is_superadmin(self):
        return self.role == 'SUPERADMIN' or self.is_superuser

    def is_admin_or_higher(self):
        return self.role in ['SUPERADMIN', 'ADMIN'] or self.is_superuser

    def is_staff_or_higher(self):
        return self.role in ['SUPERADMIN', 'ADMIN', 'STAFF'] or self.is_superuser

class SuperAdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='superadmin_profile')
    designation = models.CharField(max_length=100, default='Chief Executive Officer')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    access_level = models.IntegerField(default=10) # Highest level

    def __str__(self):
        return f"SuperAdmin: {self.user.username}"

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, default='Management')

    def __str__(self):
        return f"Admin: {self.user.username}"

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    reporting_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    shift_timing = models.CharField(max_length=50, default='9:00 AM - 6:00 PM')

    def __str__(self):
        return f"Staff: {self.user.username}"

# Signals to auto-create profiles
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'SUPERADMIN':
            SuperAdminProfile.objects.create(user=instance)
        elif instance.role == 'ADMIN':
            AdminProfile.objects.create(user=instance)
        elif instance.role == 'STAFF':
            StaffProfile.objects.create(user=instance)
        # Note: Customer profile is handled by the 'Member' model in the members app

class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
