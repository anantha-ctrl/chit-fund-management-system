from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from loans.models import Loan, EMISchedule


class LoanPayment(models.Model):
    """
    Records a single payment event against a loan.
    Can cover one or multiple EMI instalments.
    On save → signal updates EMISchedule & recalculates outstanding_balance.
    """
    PAYMENT_MODE = [
        ('cash',  'Cash'),
        ('upi',   'UPI'),
        ('bank',  'Bank Transfer'),
        ('cheque','Cheque'),
    ]

    loan = models.ForeignKey(
        Loan, on_delete=models.PROTECT,
        related_name='loanpayment_set'
    )
    emi_installment = models.ForeignKey(
        EMISchedule, on_delete=models.PROTECT,
        related_name='payments',
        null=True, blank=True,
        help_text="The specific EMI instalment this payment is against."
    )

    # ── Payment Details ─────────────────────────────
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODE, default='cash')
    transaction_reference = models.CharField(max_length=100, blank=True)
    receipt_number = models.CharField(max_length=30, unique=True, editable=False)

    # ── Penalty Info ───────────────────────────────
    penalty_waived = models.BooleanField(default=False)
    penalty_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # ── Audit ───────────────────────────────────────
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='loan_collections'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_receipt_number(self):
        from django.utils.timezone import now
        ts = now().strftime('%Y%m%d%H%M%S')
        count = LoanPayment.objects.count() + 1
        return f'RCPT-{ts}-{str(count).zfill(4)}'

    def save(self, *args, **kwargs):
        if not self.pk and not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receipt_number} | ₹{self.amount_paid} | {self.loan.loan_number}"

    class Meta:
        verbose_name = "Loan Payment"
        verbose_name_plural = "Loan Payments"
        ordering = ['-payment_date', '-created_at']


class LoanTransaction(models.Model):
    """
    Ledger record for every financial event (disbursement & collection).
    Gives a complete transaction history audit trail.
    """
    TXN_TYPE = [
        ('disbursement', 'Loan Disbursement'),
        ('collection',   'EMI Collection'),
        ('penalty',      'Penalty Collected'),
        ('topup',        'Top-Up Disbursement'),
        ('waiver',       'Penalty Waiver'),
    ]

    loan = models.ForeignKey(
        Loan, on_delete=models.PROTECT,
        related_name='transactions'
    )
    txn_type = models.CharField(max_length=20, choices=TXN_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    payment = models.ForeignKey(
        LoanPayment, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    description = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_txn_type_display()} | ₹{self.amount} | {self.loan.loan_number}"

    class Meta:
        ordering = ['-created_at']


class LoanPaymentProof(models.Model):
    """
    Allows customers to upload payment screenshots for loan EMIs.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    emi_installment = models.OneToOneField(
        EMISchedule, on_delete=models.CASCADE, related_name='proof'
    )
    member_name = models.CharField(max_length=255, blank=True, null=True)
    phone_no = models.CharField(max_length=15, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    screenshot = models.ImageField(upload_to='loan_payment_proofs/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True, null=True, help_text="Notes from the admin/staff")
    member_notes = models.TextField(blank=True, null=True, help_text="Notes from the customer")
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, 
        on_delete=models.SET_NULL, related_name='processed_loan_proofs'
    )

    def __str__(self):
        return f"Loan Proof for {self.emi_installment} - {self.transaction_id}"
