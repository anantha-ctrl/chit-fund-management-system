import csv
import os
import glob
import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import connection
from logs.models import LogEntry
from members.models import Member
from payments.models import Payment
from .models import SystemSetting

def is_superadmin(user):
    return user.is_superadmin()

# --- LOGS MANAGEMENT ---
@login_required
@user_passes_test(is_superadmin)
def log_list(request):
    logs = LogEntry.objects.all().order_by('-timestamp')[:100]
    return render(request, 'system/log_list.html', {'logs': logs})

@login_required
@user_passes_test(is_superadmin)
def clear_logs(request):
    LogEntry.objects.all().delete()
    messages.success(request, 'System Audit History purged successfully.')
    return redirect('log_list')

@login_required
def settings_view(request):
    # IF CUSTOMER -> Show Personal User Settings (Notifications, Theme, etc.)
    if request.user.role == 'CUSTOMER':
        return render(request, 'system/customer_settings.html', {'user': request.user})

    # IF ADMIN/SUPER -> Show Global System Engine (Only SuperAdmin can POST)
    essential_keys = [
        ('Company_Name', 'SmartChit Management', 'The official name of the company'),
        ('Register_Number', 'REG-10293847', 'Legal registration number of the entity'),
        ('Company_City', 'Chennai', 'City where the head office is located'),
        ('Company_State', 'Tamil Nadu', 'State where the head office is located'),
        ('GST_Number', '33AAACM1234F1Z1', 'GSTIN for tax purposes')
    ]
    
    for key, val, desc in essential_keys:
        SystemSetting.objects.get_or_create(key=key, defaults={'value': val, 'description': desc})

    # Notification Preferences (Role-based)
    alert_configs = [
        ('bi-envelope', 'Email Notifications', 'Receive weekly digest and account activity.', request.user.email_notifications, 'email_notifications'),
        ('bi-calendar-check', 'Payment Reminders', 'Get notified about upcoming payment due dates.', request.user.payment_reminders, 'payment_reminders'),
        ('bi-hammer', 'Auction Alerts', 'Real-time alerts for upcoming auction rounds.', request.user.auction_alerts, 'auction_alerts'),
        ('bi-person-plus', 'Marketing Notifications', 'Updates about new chit groups and offers.', request.user.marketing_notifications if hasattr(request.user, 'marketing_notifications') else False, 'marketing_notifications'),
    ]

    system_settings = SystemSetting.objects.all()
    if request.method == 'POST' and request.user.is_superadmin():
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                SystemSetting.objects.filter(key=key).update(value=value)
        messages.success(request, 'Global System Engine updated.')
        return redirect('system_settings_view')
    
    context = {
        'settings': system_settings,
        'alert_configs': alert_configs
    }
    return render(request, 'system/settings.html', context)

# --- EXPORT CENTER ---
@login_required
@user_passes_test(is_superadmin)
def export_dashboard(request):
    return render(request, 'system/export_center.html')

@login_required
@user_passes_test(is_superadmin)
def export_members(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="members_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Phone', 'Address', 'Status', 'Joined Date'])
    for member in Member.objects.all():
        writer.writerow([member.name, member.phone, member.full_address, member.status, member.created_at])
    return response

@login_required
@user_passes_test(is_superadmin)
def export_payments(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Member', 'Amount', 'Date', 'Status'])
    for p in Payment.objects.all():
        writer.writerow([p.member.name, p.amount, p.payment_date, p.status])
    return response

@login_required
@user_passes_test(is_superadmin)
def export_logs(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="system_audit_logs.csv"'
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'User', 'Action', 'Module', 'Details', 'IP Address'])
    for log in LogEntry.objects.all().order_by('-timestamp'):
        writer.writerow([
            log.timestamp,
            log.user.username if log.user else 'System',
            log.action,
            log.module,
            log.details,
            log.ip_address
        ])
    return response
