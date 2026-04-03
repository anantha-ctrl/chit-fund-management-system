from django.core.management.base import BaseCommand
from django.utils import timezone
from payments.models import Payment
from decimal import Decimal

class Command(BaseCommand):
    help = 'Calculates daily penalties for overdue payments'

    def handle(self, *args, **options):
        today = timezone.now().date()
        overdue_payments = Payment.objects.filter(
            status='PENDING',
            due_date__lt=today
        )

        count = 0
        for payment in overdue_payments:
            # Example penalty logic: 1% of installment amount for every 5 days overdue
            # or a fixed daily penalty of ₹5
            days_overdue = (today - payment.due_date).days
            
            # Simple daily flat penalty for demonstration
            daily_rate = Decimal('5.00') 
            new_penalty = daily_rate * days_overdue
            
            if payment.penalty_amount != new_penalty:
                payment.penalty_amount = new_penalty
                payment.save()
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully updated penalties for {count} payments'))
