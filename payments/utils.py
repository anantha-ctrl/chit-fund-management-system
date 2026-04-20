from datetime import date
from decimal import Decimal
from .models import Payment

def update_penalties():
    """
    Updates penalties for all 'PENDING' or 'LATE' payments that are past their due date.
    Calculates penalty based on ChitGroup settings.
    """
    today = date.today()
    # Filter payments that are pending or late and have a due date in the past
    overdue_payments = Payment.objects.filter(due_date__lt=today).exclude(status='PAID')

    updated_count = 0
    for payment in overdue_payments:
        group = payment.chit_group
        if group.penalty_per_day > 0:
            # Mark as late if not already
            if payment.status != 'LATE':
                payment.status = 'LATE'
            
            # Calculate days overdue
            days_overdue = (today - payment.due_date).days
            
            # Penalty amount = days * penalty_per_day
            # You could also add a fixed penalty if desired
            payment.penalty_amount = Decimal(days_overdue) * group.penalty_per_day
            payment.save()
            updated_count += 1
    
    return updated_count
