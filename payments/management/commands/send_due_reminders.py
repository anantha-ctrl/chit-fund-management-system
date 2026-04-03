from django.core.management.base import BaseCommand
from django.utils import timezone
from payments.models import Payment
from notifications.utils import send_payment_reminder
import datetime

class Command(BaseCommand):
    help = 'Sends automated SMS reminders to members for upcoming and overdue payments'

    def handle(self, *args, **options):
        today = timezone.now().date()
        # Find payments due in the next 3 days OR overdue payments
        target_span = today + datetime.timedelta(days=3)
        
        pending_payments = Payment.objects.filter(
            status__in=['PENDING', 'LATE'],
            due_date__lte=target_span
        ).select_related('member', 'chit_group')

        sent_count = 0
        error_count = 0
        
        for payment in pending_payments:
            try:
                success = send_payment_reminder(payment)
                if success:
                    sent_count += 1
                else:
                    error_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error sending to {payment.member.name}: {str(e)}"))
                error_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Bulk Reminders Finished: {sent_count} sent successfully, {error_count} failed."
        ))
