from django.db import models
from members.models import Member
from chits.models import ChitGroup

class Settlement(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    chit_group = models.ForeignKey(ChitGroup, on_delete=models.CASCADE)
    
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_received = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    dividend = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    penalty = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('member', 'chit_group')
        
    def save(self, *args, **kwargs):
        # Calculate net_amount = total_received + dividend - (total_paid + penalty)
        self.net_amount = (self.total_received + self.dividend) - (self.total_paid + self.penalty)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Settlement {self.member.name} - {self.chit_group.name}"
