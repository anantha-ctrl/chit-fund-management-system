import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Override settings for the check to avoid hanging
from django.conf import settings
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import pymysql
    pymysql.version_info = (2, 2, 1, 'final', 0)
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# Set a timeout for the connection
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'chit_fund_db'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'connect_timeout': 5,
        }
    }
}
settings.configure(DATABASES=DATABASES, INSTALLED_APPS=[
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'members',
    'chits',
    'payments',
    'auctions',
    'settlements',
    'branches',
    'system_settings',
    'logs',
    'notifications',
    'reports_export',
    'loan_customers',
    'loans',
    'loan_payments',
    'loan_reports',
])

try:
    print("Initializing Django (with 5s Timeout)...")
    django.setup()
    
    from django.db import connection
    print("Attempting to connect to the database (with 5s timeout)...")
    
    # We can pass connection options temporarily for testing
    connection.ensure_connection()
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        row = cursor.fetchone()
        print(f"Database Connection SUCCESS: {row}")
        
    print("Checking for migrations...")
    from django.core.management import call_command
    call_command('showmigrations')
    
except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nAll checks passed!")
