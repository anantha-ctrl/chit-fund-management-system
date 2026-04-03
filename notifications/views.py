from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
        
        count = 0
        for user in users:
            Notification.objects.create(
                user=user,
                title=title,
                message=message,
                priority=priority
            )
            count += 1
            
        messages.success(request, f'Notification successfully blasted to {count} users via Portal & SMS/WhatsApp Queue.')
        return redirect('bulk_notification')
        
    return render(request, 'notifications/bulk_notification.html', {
        'title': 'Bulk Member Communication Hub'
    })
