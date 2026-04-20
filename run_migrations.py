import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Chit_Fund_Management.settings')
django.setup()

try:
    print("Making migrations...")
    call_command('makemigrations', 'loan_payments')
    print("Migrating...")
    call_command('migrate', 'loan_payments')
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
