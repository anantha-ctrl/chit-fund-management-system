import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User

# Check if admin already exists
if User.objects.filter(username='admin').exists():
    u = User.objects.get(username='admin')
    u.password = 'admin123' # Explicitly raw
    u.is_superuser = True
    u.is_staff = True
    u.role = 'SUPERADMIN'
    u.save()
    print("Updated existing user 'admin' with RAW password 'admin123'")
else:
    u = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin123', role='SUPERADMIN')
    print("Created new superadmin 'admin' with RAW password 'admin123'")
