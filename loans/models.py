from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import math

from branches.models import Branch


class Loan(models.Model):
    """
    Core Loan record. Supports standard EMI loans and top-up loans.
    EMI is calculated using the standard reducing-balance formula:
        EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    where r = monthly interest rate, n = tenure in months.
    """
    STATUS_CHOICES = [
        ('pending',  'Pending Approval'),
        ('approved', 'Approved'),
        ('active',   'Active / Disbursed'),
        ('closed',   'Closed'),
        ('default',  'Default'),
        ('rejected', 'Rejected'),
    ]
    INTEREST_TYPE_CHOICES = [
        ('reducing', 'Reducing Balance'),
        ('flat',     'Flat Rate'),
    ]
    LOAN_TYPE_CHOICES = [
        ('personal', 'Personal Loan'),
        ('home',     'Home Loan'),
        ('gold',     'Gold Loan'),
        ('vehicle',  'Vehicle Loan'),
        ('property', 'Property Loan'),
        ('business', 'Business Loan'),
        ('education','Education Loan'),
        ('other',    'Other'),
    ]

    # ── Relationships ──────────────────────────────
    customer = models.ForeignKey(
        'members.Member', on_delete=models.PROTECT, related_name='loan_set'
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.PROTECT, related_name='loans'
    )
    parent_loan = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='top_up_loans',
        help_text="Set if this is a top-up on an existing loan."
    )

    # ── Loan Terms ─────────────────────────────────
    loan_number = models.CharField(max_length=20, unique=True, editable=False)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Annual interest rate in %"
    )
    interest_type = models.CharField(
        max_length=10, choices=INTEREST_TYPE_CHOICES, default='reducing'
    )
    tenure_months = models.PositiveIntegerField(help_text="Loan tenure in months")
    start_date = models.DateField()
    loan_type = models.CharField(
        max_length=20, choices=LOAN_TYPE_CHOICES, default='personal',
        help_text="Select the category of loan"
    )

    # ── Calculated Fields (auto-populated on save) ─
    emi_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    total_interest = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    total_payable = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    outstanding_balance = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    # ── Approval Workflow ──────────────────────────
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='loans_approved'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # ── Disbursement ───────────────────────────────
    disbursed_at = models.DateTimeField(null=True, blank=True)
    disbursement_mode = models.CharField(
        max_length=20,
        choices=[('cash', 'Cash'), ('bank', 'Bank Transfer'), ('upi', 'UPI')],
        blank=True
    )
    disbursement_reference = models.CharField(max_length=100, blank=True)

    # ── Penalty Settings ───────────────────────────
    penalty_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('2.00'),
        help_text="Penalty % per month on overdue EMI principal"
    )
    grace_period_days = models.PositiveIntegerField(
        default=5, help_text="Grace days before penalty is applied"
    )

    # ── Audit ──────────────────────────────────────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='loans_created'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ──────────────────────────────────────────────
    # BUSINESS LOGIC — EMI CALCULATION
    # ──────────────────────────────────────────────

    def calculate_emi(self):
        """
        Standard EMI formula (Reducing Balance):
            EMI = P * r * (1+r)^n / ((1+r)^n - 1)
        Flat Rate:
            EMI = (P + P*R*N/12) / N
        """
        P = float(self.loan_amount)
        N = int(self.tenure_months)
        annual_rate = float(self.interest_rate)

        if self.interest_type == 'reducing':
            r = annual_rate / 12 / 100  # monthly rate
            if r == 0:
                emi = P / N
            else:
                emi = P * r * math.pow(1 + r, N) / (math.pow(1 + r, N) - 1)
            total_payable = emi * N
            total_interest = total_payable - P
        else:  # flat rate
            total_interest = P * annual_rate * N / (12 * 100)
            total_payable = P + total_interest
            emi = total_payable / N

        return {
            'emi': round(Decimal(str(emi)), 2),
            'total_interest': round(Decimal(str(total_interest)), 2),
            'total_payable': round(Decimal(str(total_payable)), 2),
        }

    def generate_emi_number(self):
        """Auto-generate a unique loan number like LN-2024-0001."""
        from django.utils.timezone import now
        year = now().year
        prefix = f'LN-{year}-'
        last_loan = Loan.objects.filter(loan_number__startswith=prefix).order_by('loan_number').last()
        
        if last_loan:
            try:
                last_num = int(last_loan.loan_number.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1
            
        return f'{prefix}{str(new_num).zfill(4)}'

    def save(self, *args, **kwargs):
        # Auto-generate loan number on first save
        if not self.pk and not self.loan_number:
            self.loan_number = self.generate_emi_number()

        # Calculate EMI amounts whenever loan is saved
        calc = self.calculate_emi()
        self.emi_amount = calc['emi']
        self.total_interest = calc['total_interest']
        self.total_payable = calc['total_payable']

        # Set outstanding balance = total payable on creation
        if not self.pk:
            self.outstanding_balance = calc['total_payable']

        super().save(*args, **kwargs)

    def approve(self, user):
        """Approve a pending loan."""
        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()

    def disburse(self, mode='cash', reference=''):
        """Mark loan as active/disbursed."""
        self.status = 'active'
        self.disbursed_at = timezone.now()
        self.disbursement_mode = mode
        self.disbursement_reference = reference
        self.save()

    def reject(self, reason=''):
        """Reject a loan application."""
        self.status = 'rejected'
        self.rejection_reason = reason
        self.save()

    @property
    def is_overdue(self):
        """True if any EMI is overdue."""
        return self.emi_schedule.filter(status='overdue').exists()

    @property
    def paid_emis(self):
        return self.emi_schedule.filter(status='paid').count()

    @property
    def pending_emis(self):
        return self.emi_schedule.filter(status__in=['pending', 'overdue']).count()

    @property
    def completion_pct(self):
        total = self.emi_schedule.count()
        if total == 0:
            return 0
        return int((self.paid_emis / total) * 100)

    def __str__(self):
        return f"{self.loan_number} — {self.customer.name}"

    class Meta:
        verbose_name = "Loan"
        verbose_name_plural = "Loans"
        ordering = ['-created_at']


class EMISchedule(models.Model):
    """
    One row per EMI installment.
    Generated automatically when a loan is activated/disbursed.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid',    'Paid'),
        ('overdue', 'Overdue'),
        ('partial', 'Partially Paid'),
        ('waived',  'Waived'),
    ]

    loan = models.ForeignKey(
        Loan, on_delete=models.CASCADE, related_name='emi_schedule'
    )
    installment_number = models.PositiveIntegerField()
    due_date = models.DateField()

    # ── Amounts ────────────────────────────────────
    emi_amount = models.DecimalField(max_digits=12, decimal_places=2)
    principal_component = models.DecimalField(max_digits=12, decimal_places=2)
    interest_component = models.DecimalField(max_digits=12, decimal_places=2)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2)
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2)

    # ── Payment Tracking ───────────────────────────
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_date = models.DateField(null=True, blank=True)
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.loan.loan_number} — EMI #{self.installment_number}"

    @property
    def balance_due(self):
        return self.emi_amount + self.penalty_amount - self.paid_amount

    @property
    def dynamic_status(self):
        """
        Determines the real-time status:
        - PAID: If status is paid
        - OPEN: If it's the current month and today is <= 10th
        - OVERDUE: If it's past month or current month > 10th and unpaid
        - UPCOMING: Future months
        """
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.status == 'paid':
            return 'PAID'
            
        # Current month logic
        if self.due_date.year == today.year and self.due_date.month == today.month:
            return 'OPEN' if today.day <= 10 else 'OVERDUE'
            
        # Past logic
        if self.due_date < today:
            return 'OVERDUE'
            
        return 'UPCOMING'

    class Meta:
        unique_together = ['loan', 'installment_number']
        ordering = ['installment_number']
