from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Loan


@receiver(post_save, sender=Loan)
def on_loan_status_change(sender, instance, created, **kwargs):
    """
    When a loan transitions to 'active', automatically generate
    the full EMI schedule if it doesn't already exist.
    """
    # Generate schedule if it doesn't exist yet (for most statuses)
    if instance.status not in ['rejected', 'closed'] and not instance.emi_schedule.exists():
        from .utils import generate_emi_schedule
        generate_emi_schedule(instance)
