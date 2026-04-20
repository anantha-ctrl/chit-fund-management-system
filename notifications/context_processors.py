from .models import Notification
from django.utils import timezone

def notifications_status(request):
    """Provides global notification counts for all templates"""
    if request.user.is_authenticated:
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        today_notifications_count = unread_notifications.filter(created_at__gte=today_start).count()
        
        return {
            'notifications': unread_notifications[:5],
            'today_notifications_count': today_notifications_count,
            'unread_count': unread_notifications.count()
        }
    return {
        'notifications': [],
        'today_notifications_count': 0,
        'unread_count': 0
    }
