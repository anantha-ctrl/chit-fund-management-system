from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import LogEntry

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # Get IP Address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
        
    LogEntry.objects.create(
        user=user,
        action='LOGIN',
        module='Authentication',
        details=f'User {user.username} successfully logged into the system.',
        ip_address=ip
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        LogEntry.objects.create(
            user=user,
            action='LOGOUT',
            module='Authentication',
            details=f'User {user.username} logged out of the session.'
        )
