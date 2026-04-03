from django.db import models
from accounts.models import User

class LogEntry(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('LOGIN', 'Logged In'),
        ('LOGOUT', 'Logged Out'),
        ('TRANSACTION', 'Financial Transaction'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='system_log_entries')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    module = models.CharField(max_length=50) # e.g., 'Members', 'Payments'
    details = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} on {self.module} at {self.timestamp}"

    class Meta:
        verbose_name_plural = "Log Entries"
        ordering = ['-timestamp']
