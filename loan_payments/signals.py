from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from .models import LoanPayment, LoanTransaction
from loans.models import EMISchedule


@receiver(post_save, sender=LoanPayment)
def on_payment_saved(sender, instance, created, **kwargs):
    """
    After a payment is saved:
    1. Update the linked EMI instalment status (paid / partial / overdue).
    2. Recalculate the loan's outstanding balance.
    3. Log a LoanTransaction ledger entry.
    """
    if not created:
        return  # Only process on new payment creation

    payment = instance
    loan = payment.loan

    # ── Step 1: Update EMI Instalment ──────────────────
    emi = payment.emi_installment
    if emi:
        emi.paid_amount += payment.amount_paid
        emi.penalty_paid = payment.penalty_paid if not payment.penalty_waived else Decimal('0.00')
        emi.paid_date = payment.payment_date

        total_due = emi.emi_amount + emi.penalty_amount
        if payment.penalty_waived:
            emi.penalty_amount = Decimal('0.00')

        if emi.paid_amount >= emi.emi_amount:
            emi.status = 'paid'
        elif emi.paid_amount > 0:
            emi.status = 'partial'

        emi.save(update_fields=['paid_amount', 'paid_date', 'status', 'penalty_amount'])

    # ── Step 2: Recalculate outstanding balance ─────────
    from loans.utils import recalculate_outstanding
    recalculate_outstanding(loan)

    # ── Step 3: Log transaction in ledger ───────────────
    LoanTransaction.objects.create(
        loan=loan,
        txn_type='collection',
        amount=payment.amount_paid,
        balance_after=loan.outstanding_balance,
        payment=payment,
        description=f"EMI #{emi.installment_number if emi else '—'} collected via {payment.get_payment_mode_display()}",
        created_by=payment.collected_by,
    )
    if payment.penalty_paid > 0:
        LoanTransaction.objects.create(
            loan=loan,
            txn_type='penalty',
            amount=payment.penalty_paid,
            balance_after=loan.outstanding_balance,
            payment=payment,
            description=f"Penalty collected for EMI #{emi.installment_number if emi else '—'}",
            created_by=payment.collected_by,
        )
