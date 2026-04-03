from django.db import models
from members.models import Member
from decimal import Decimal

class ChitGroup(models.Model):
    name = models.CharField(max_length=150)
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='chit_groups')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    duration_months = models.IntegerField()
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('ACTIVE', 'Active'), ('COMPLETED', 'Completed')], default='ACTIVE')
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    members = models.ManyToManyField(Member, through='ChitMember')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class ChitMember(models.Model):
    chit_group = models.ForeignKey(ChitGroup, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    joined_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('chit_group', 'member')
