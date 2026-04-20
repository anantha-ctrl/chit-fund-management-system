from django.db import models
from members.models import Member
from chits.models import ChitGroup
from accounts.models import User

class Payment(models.Model):
    STATUS_CHOICES = (
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
        ('LATE', 'Late'),
        ('AWAITING_VERIFICATION', 'Awaiting Verification'),
    )

    chit_group = models.ForeignKey(ChitGroup, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    installment_number = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING')
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    dividend_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    collected_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='collections')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chit_group', 'member', 'installment_number')
        
    def __str__(self):
        return f"{self.member.name} - {self.chit_group.name} - {self.installment_number}"

    @property
    def net_amount(self):
        """Calculates the actual payable amount for the member"""
        return (self.amount - self.dividend_amount) + self.penalty_amount

    @property
    def dynamic_status(self):
        """
        Determines the real-time status for chit installments.
        """
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.status == 'PAID':
            return 'PAID'
            
        if not self.due_date:
            return 'UPCOMING'
            
        # Current month logic
        if self.due_date.year == today.year and self.due_date.month == today.month:
            return 'OPEN' if today.day <= 10 else 'OVERDUE'
            
        # Past logic
        if self.due_date < today:
            return 'OVERDUE'
            
        return 'UPCOMING'

class PaymentProof(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='proof')
    member_name = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=15)
    transaction_id = models.CharField(max_length=100, unique=True)
    screenshot = models.ImageField(upload_to='payment_proofs/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='processed_proofs')

    def __str__(self):
        return f"Proof for {self.payment} - {self.transaction_id}"

class CashHandover(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='handovers')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff.username} - ₹{self.amount} - {self.status}"

class FollowUp(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='follow_ups')
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_follow_ups')
    note = models.TextField()
    reminder_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.name} - {self.reminder_date}"

class PaymentQR(models.Model):
    name = models.CharField(max_length=100, default="Primary QR Code")
    qr_code = models.ImageField(upload_to='system/qr_codes/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
