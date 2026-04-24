import os
import sys

# ───── FIX: Add project root to Python path ─────
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# ────────────────────────────────────────────────

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
