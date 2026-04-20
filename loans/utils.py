from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from .models import EMISchedule


def generate_emi_schedule(loan):
    """
    Generate the full EMI repayment schedule for a loan using the
    Reducing Balance method (amortisation table).

    For each installment:
      - Interest component = opening_balance * monthly_rate
      - Principal component = EMI - interest_component
      - Closing balance = opening_balance - principal_component

    This is stored in EMISchedule so staff can track each due date.
    """
    # Delete any existing schedule (e.g. recalculation after top-up)
    loan.emi_schedule.all().delete()

    P = float(loan.loan_amount)
    N = int(loan.tenure_months)
    annual_rate = float(loan.interest_rate)
    monthly_rate = annual_rate / 12 / 100
    emi = float(loan.emi_amount)
    start_date = loan.start_date

    opening_balance = P
    schedule = []

    for i in range(1, N + 1):
        # Due date = start_date + i months
        due_date = start_date + relativedelta(months=i)

        if loan.interest_type == 'reducing':
            interest_component = opening_balance * monthly_rate
            principal_component = emi - interest_component
        else:
            # Flat rate: interest is same every month
            interest_component = P * annual_rate / (12 * 100)
            principal_component = P / N

        closing_balance = max(opening_balance - principal_component, 0)

        schedule.append(EMISchedule(
            loan=loan,
            installment_number=i,
            due_date=due_date,
            emi_amount=round(Decimal(str(emi)), 2),
            principal_component=round(Decimal(str(principal_component)), 2),
            interest_component=round(Decimal(str(interest_component)), 2),
            opening_balance=round(Decimal(str(opening_balance)), 2),
            closing_balance=round(Decimal(str(closing_balance)), 2),
            status='pending',
        ))

        opening_balance = closing_balance

    # Bulk create for performance
    EMISchedule.objects.bulk_create(schedule)
    return schedule


def mark_overdue_emis():
    """
    Utility function — call from a management command or cron job daily.
    Marks all pending EMIs past their due date as 'overdue' and calculates penalty.
    """
    today = date.today()
    overdue_emis = EMISchedule.objects.filter(
        status='pending',
        due_date__lt=today
    ).select_related('loan')

    updated = []
    for emi in overdue_emis:
        days_late = (today - emi.due_date).days
        grace = emi.loan.grace_period_days
        if days_late > grace:
            emi.status = 'overdue'
            # Penalty = principal_component * penalty_rate% * months_overdue
            months_late = max(1, days_late // 30)
            penalty = (
                emi.principal_component
                * (emi.loan.penalty_rate / 100)
                * months_late
            )
            emi.penalty_amount = round(penalty, 2)
            updated.append(emi)

    if updated:
        EMISchedule.objects.bulk_update(updated, ['status', 'penalty_amount'])

    return len(updated)


def recalculate_outstanding(loan):
    """
    Recalculate outstanding_balance on a loan from the EMI schedule.
    Called after every payment.
    """
    from .models import Loan
    unpaid = loan.emi_schedule.filter(
        status__in=['pending', 'overdue', 'partial']
    )
    total_due = sum(
        (e.emi_amount + e.penalty_amount - e.paid_amount) for e in unpaid
    )
    loan.outstanding_balance = max(Decimal('0.00'), total_due)

    # Auto-close loan if all EMIs are paid
    if loan.emi_schedule.filter(status__in=['pending', 'overdue', 'partial']).count() == 0:
        loan.status = 'closed'

    loan.save(update_fields=['outstanding_balance', 'status'])
