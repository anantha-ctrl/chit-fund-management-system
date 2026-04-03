from django.db import models
from members.models import Member
from chits.models import ChitGroup

class Payment(models.Model):
    STATUS_CHOICES = (
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
        ('LATE', 'Late'),
    )

    chit_group = models.ForeignKey(ChitGroup, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    installment_number = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    dividend_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chit_group', 'member', 'installment_number')
        
    def __str__(self):
        return f"{self.member.name} - {self.chit_group.name} - {self.installment_number}"
