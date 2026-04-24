
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from chits.models import ChitGroup
try:
    g = ChitGroup.objects.get(name='Gold')
    print(f'Group: {g.name}')
    print(f'Total Members: {g.members.count()}')
except Exception as e:
    print(f'Error: {e}')
