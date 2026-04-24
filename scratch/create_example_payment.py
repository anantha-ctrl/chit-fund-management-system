
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from chits.models import ChitGroup
from members.models import Member
from payments.models import Payment

try:
    group = ChitGroup.objects.get(name='Gold')
    member = Member.objects.get(name='Jessica')
    
    # Create Month 3 as a realistic example
    # Base: 1000, Dividend: 100, Net: 900
    payment, created = Payment.objects.get_or_create(
        chit_group=group,
        member=member,
        installment_number=3,
        defaults={
            'amount': 1000,
            'dividend_amount': 100,
            'due_date': date.today() + timedelta(days=30),
            'status': 'PENDING'
        }
    )
    
    if not created:
        payment.amount = 1000
        payment.dividend_amount = 100
        payment.status = 'PENDING'
        payment.save()
        
    print(f"Successfully created Example Month 3 for Jessica in Gold Group.")
    print(f"Base: 1000, Dividend: 100 -> Expected Payout: 900")
except Exception as e:
    print(f"Error: {e}")
