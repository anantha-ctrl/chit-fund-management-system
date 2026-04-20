from django.db import models
from django.conf import settings
from branches.models import Branch


class LoanAgent(models.Model):
    """
    Agent model for loan business – separate from chit fund agents.
    Links a system user to a branch as a loan field agent.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loan_agent_profile'
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='loan_agents'
    )
    employee_code = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    joined_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_code})"

    @property
    def customer_count(self):
        return self.assigned_members.count()

    @property
    def active_loans_count(self):
        from loans.models import Loan
        return Loan.objects.filter(customer__loan_agent=self, status='active').count()

    @property
    def overdue_count(self):
        from loans.models import EMISchedule
        return EMISchedule.objects.filter(loan__customer__loan_agent=self, status='overdue').count()

    class Meta:
        verbose_name = "Loan Agent"
        verbose_name_plural = "Loan Agents"
        ordering = ['user__first_name']


# LoanCustomer model has been unified into members.Member

