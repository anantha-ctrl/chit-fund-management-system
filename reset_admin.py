import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User

# Delete existing admin to be 100% sure we start fresh
User.objects.filter(username='admin').delete()

# Create new superadmin
# NOTE: User.objects.create_superuser() will use our OVERRIDDEN set_password()
# which saves it as RAW text.
admin = User.objects.create_superuser(
    username='admin',
    email='admin@gmail.com',
    password='admin123',
    role='SUPERADMIN'
)

# Explicitly ensure password is set to raw one more time
admin.password = 'admin123'
admin.is_active = True
admin.save()

print(f"Successfully RECREATED 'admin' with RAW password 'admin123'")
print(f"User in DB: {admin.username}, Password: {admin.password}")
print(f"Is Active: {admin.is_active}")
