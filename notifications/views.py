from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
import csv
from django.http import HttpResponse
from .models import Notification

@login_required
def notification_list(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/notification_list.html', {'notifications': notifs})

@login_required
def toggle_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = not notif.is_read
    notif.save()
    return redirect(request.META.get('HTTP_REFERER', 'notification_list'))

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notification_list')

@login_required
def delete_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.delete()
    messages.success(request, 'Notification deleted.')
    return redirect('notification_list')

@login_required
def mark_individual_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def delete_all_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    messages.success(request, 'All notifications cleared.')
    return redirect('notification_list')

from accounts.models import User
from django.contrib.auth.decorators import user_passes_test

def is_superadmin(user):
    return user.is_superadmin()

@login_required
@user_passes_test(is_superadmin)
def bulk_notification_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        priority = request.POST.get('priority', 'info')
        
        # Get all users (or filter if needed)
        users = User.objects.filter(is_active=True)
        
        from django.core.mail import send_mail
        from django.conf import settings
        
        count = 0
        email_list = []
        for user in users:
            Notification.objects.create(
                user=user,
                title=title,
                message=message,
                priority=priority
            )
            if user.email:
                email_list.append(user.email)
            count += 1
            
        # Send bulk email if recipients exist
        if email_list:
            try:
                send_mail(
                    subject=f"SmartChit Broadcast: {title}",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=email_list,
                    fail_silently=True
                )
            except Exception as e:
                print(f"Bulk email error: {e}")
            
        messages.success(request, f'Broadcast successfully dispatched to {count} users via Portal & Email.')
        return redirect('bulk_notification')
    
    # Get history of unique bulk notifications sent (grouped loosely by title and message)
    # This is a workaround since we don't have a BulkNotification table
    sent_history = Notification.objects.values('title', 'message', 'priority', 'created_at__date').annotate(count=models.Count('id')).order_by('-created_at__date')[:10]
    
    total_reach = User.objects.filter(is_active=True).count()
        
    return render(request, 'notifications/bulk_notification.html', {
        'title': 'Bulk Member Communication Hub',
        'sent_history': sent_history,
        'total_reach': total_reach
    })

@login_required
@user_passes_test(is_superadmin)
def export_notification_logs(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="broadcast_logs.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Title', 'Message', 'Priority', 'Recipient/Status'])
    
    # Using the same grouping logic as the history table
    logs = Notification.objects.all().order_by('-created_at')
    
    for log in logs:
        writer.writerow([
            log.created_at.strftime("%Y-%m-%d %H:%M"),
            log.title,
            log.message,
            log.priority,
            log.user.username
        ])
    
    return response
