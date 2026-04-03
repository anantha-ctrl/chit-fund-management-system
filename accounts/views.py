from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
import random
import string
from members.models import Member, MemberDocument
from members.views import MemberDocumentForm
import datetime
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm, UserProfileUpdateForm

def is_superadmin(user):
    return user.is_superadmin()

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            print(f"DEBUG LOGIN VIEW: Success login for {user.username}")
            return redirect('dashboard')
        else:
            print(f"DEBUG LOGIN VIEW ERRORS: {form.errors}")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing')

@login_required
def dashboard_view(request):
    from members.models import Member
    from chits.models import ChitGroup, ChitMember
    from payments.models import Payment
    from auctions.models import Auction
    from branches.models import Branch
    from logs.models import LogEntry
    from notifications.models import Notification
    from django.db.models import Sum, Count
    from django.utils import timezone
    import datetime
    
    now = timezone.now()
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]

    # CUSTOMER PERSONALIZED DASHBOARD
    if request.user.role == 'CUSTOMER' and hasattr(request.user, 'member_profile'):
        member = request.user.member_profile
        my_chit_members = ChitMember.objects.filter(member=member)
        my_groups_count = my_chit_members.count()
        
        total_paid = Payment.objects.filter(member=member, status='PAID').aggregate(Sum('amount'))['amount__sum'] or 0
        total_pending = Payment.objects.filter(member=member, status__in=['PENDING', 'LATE']).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Projection for "Again Upcoming" if no pending exists
        upcoming_projection = 0
        if total_pending == 0:
            for mc in my_chit_members:
                if mc.chit_group.status == 'ACTIVE':
                    upcoming_projection += mc.chit_group.installment_amount
        
        display_pending = total_pending if total_pending > 0 else upcoming_projection
        
        recent_my_payments = Payment.objects.filter(member=member).order_by('-payment_date')[:5]
        
        relevant_group_ids = my_chit_members.values_list('chit_group_id', flat=True)
        recent_group_auctions = Auction.objects.filter(chit_group_id__in=relevant_group_ids).order_by('-auction_date')[:5]

        context = {
            'role': 'CUSTOMER',
            'my_groups_count': my_groups_count,
            'total_paid': total_paid,
            'total_pending': display_pending,
            'recent_payments': recent_my_payments,
            'recent_auctions': recent_group_auctions,
            'notifications': notifications,
        }
        return render(request, 'accounts/customer/dashboard.html', context)

    # ADMIN / STAFF DASHBOARD (Full/Shared)
    try:
        # Get period filter (default to 6 months)
        period = request.GET.get('period', '6m')
        
        # Calculate start date based on period
        if period == '1m':
            months_back = 1
            period_label = 'Current Month'
        elif period == '3m':
            months_back = 3
            period_label = 'Last 3 Months'
        else:
            months_back = 6
            period_label = 'Last 6 Months'
            
        # Collection Logic
        total_received = Payment.objects.filter(status='PAID').aggregate(Sum('amount'))['amount__sum'] or 0
        total_pending = Payment.objects.filter(status__in=['PENDING', 'LATE']).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Monthly Collection Trend based on selected period
        chart_labels = []
        chart_data = []
        for i in range(months_back - 1, -1, -1):
            # Calculate month for the iteration
            target_date = now - datetime.timedelta(days=i*30)
            month_label = target_date.strftime('%b')
            month_sum = Payment.objects.filter(
                status='PAID', 
                payment_date__year=target_date.year, 
                payment_date__month=target_date.month
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            chart_labels.append(month_label)
            chart_data.append(float(month_sum))

        # Group Distribution (Doughnut Chart)
        group_dist = ChitGroup.objects.values('amount').annotate(count=Count('id'))
        group_labels = [f"₹{int(g['amount'])}" for g in group_dist]
        group_counts = [g['count'] for g in group_dist]

        context = {
            'role': request.user.role,
            'total_members': Member.objects.count(),
            'active_chits': ChitGroup.objects.filter(status='ACTIVE').count(),
            'total_branches': Branch.objects.count(),
            'total_auctions': Auction.objects.count(),
            'total_received': total_received,
            'total_pending': total_pending,
            'recent_payments': Payment.objects.select_related('member').order_by('-payment_date')[:5],
            'upcoming_auctions': Auction.objects.filter(auction_date__gte=now).order_by('auction_date')[:5],
            'recent_logs': LogEntry.objects.all().order_by('-timestamp')[:8],
            'notifications': notifications,
            
            # Chart & Filter Info
            'chart_labels': chart_labels,
            'chart_data': chart_data,
            'group_labels': group_labels,
            'group_counts': group_counts,
            'performance_percent': round((total_received / (total_received + total_pending)) * 100, 1) if (total_received + total_pending) > 0 else 0,
            'active_period': period,
            'period_label': period_label
        }
    except Exception as e:
        context = {'role': request.user.role, 'notifications': notifications, 'error': str(e)}
        
    return render(request, 'dashboard.html', context)

@login_required
def customer_reports_view(request):
    # Only for customers
    if request.user.role != 'CUSTOMER' or not hasattr(request.user, 'member_profile'):
        messages.error(request, 'This view is only available for active Customer accounts.')
        return redirect('dashboard')
    
    from django.db.models import Sum
    from payments.models import Payment
    from chits.models import ChitGroup
    member = request.user.member_profile
    my_chits = member.chitmember_set.all()
    
    # Financial Summary
    total_paid = Payment.objects.filter(member=member, status='PAID').aggregate(Sum('amount'))['amount__sum'] or 0
    total_pending = Payment.objects.filter(member=member, status__in=['PENDING', 'LATE']).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Logic for "Again Upcoming" - Project the next month's installment if current is paid
    upcoming_projection = 0
    if total_pending == 0:
        for mc in my_chits:
            if mc.chit_group.status == 'ACTIVE':
                # Projection: Full installment amount for the next month
                upcoming_projection += mc.chit_group.installment_amount
    
    display_pending = total_pending if total_pending > 0 else upcoming_projection
    
    # Detailed breakdown per chit
    chit_breakdown = []
    active_chit_names = []
    for mc in my_chits:
        group = mc.chit_group
        if group.status == 'ACTIVE':
            active_chit_names.append(group.name)
            
        paid_in_group = Payment.objects.filter(member=member, chit_group=group, status='PAID').aggregate(Sum('amount'))['amount__sum'] or 0
        
        chit_breakdown.append({
            'group_name': group.name,
            'chit_value': group.amount,
            'paid_amount': paid_in_group,
            'status': group.status
        })

    # Header Name Logic
    report_title = "Financial Summary"
    if len(active_chit_names) == 1:
        report_title = f"Report: {active_chit_names[0]}"

    context = {
        'total_paid': total_paid,
        'total_pending': display_pending,
        'chit_breakdown': chit_breakdown,
        'member': member,
        'report_title': report_title
    }
    return render(request, 'accounts/customer/reports.html', context)

@login_required
def customer_documents_view(request):
    """View for Customers to upload and track their own KYC documents"""
    if request.user.role != 'CUSTOMER' or not hasattr(request.user, 'member_profile'):
        messages.error(request, 'Profile not found.')
        return redirect('dashboard')
    
    member = request.user.member_profile
    documents = member.documents.all().order_by('-uploaded_at')
    
    if request.method == 'POST':
        form = MemberDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.member = member
            doc.status = 'PENDING' # Explicitly set to pending on new upload
            doc.save()
            messages.success(request, 'Document uploaded successfully! It is now pending verification by the admin.')
            return redirect('customer_documents')
    else:
        form = MemberDocumentForm()
    
    return render(request, 'accounts/customer/documents.html', {
        'documents': documents,
        'form': form,
        'member': member
    })

@login_required
@user_passes_test(lambda u: u.is_admin_or_higher())
def admin_approve_document(request, pk, action):
    """View for Admins to Approve or Reject documents"""
    doc = get_object_or_404(MemberDocument, pk=pk)
    
    if action == 'approve':
        doc.status = 'APPROVED'
        doc.verified_at = timezone.now()
        messages.success(request, f'Document for {doc.member.name} has been APPROVED.')
    elif action == 'reject':
        doc.status = 'REJECTED'
        reason = request.POST.get('rejection_reason', 'Document details are unclear or incorrect.')
        doc.admin_notes = reason
        messages.warning(request, f'Document for {doc.member.name} has been REJECTED.')
    
    doc.save()
    return redirect('member_detail', pk=doc.member.id)

@login_required
def reports_view(request):
    try:
        from payments.models import Payment
        from django.db.models import Sum
        late_payments = Payment.objects.filter(status='LATE')
        recent_payments = Payment.objects.filter(status='PAID').order_by('-payment_date')[:10]
        
        total_late = late_payments.aggregate(Sum('amount'))['amount__sum'] or 0
        total_collected = Payment.objects.filter(status='PAID').aggregate(Sum('amount'))['amount__sum'] or 0
        defaulter_count = late_payments.values('member').distinct().count()
        # Efficiency calculation
        total_potential = total_collected + total_late
        efficiency = (total_collected / total_potential * 100) if total_potential > 0 else 100
        
        # Branch Performance
        from branches.models import Branch
        from members.models import Member
        branches = Branch.objects.all()
        branch_stats = []
        for branch in branches:
            branch_collected = Payment.objects.filter(member__branch=branch, status='PAID').aggregate(Sum('amount'))['amount__sum'] or 0
            branch_member_count = Member.objects.filter(branch=branch).count()
            branch_stats.append({
                'name': branch.name,
                'total_collected': branch_collected,
                'member_count': branch_member_count
            })
            
    except Exception as e:
        late_payments = []
        recent_payments = []
        total_late = 0
        total_collected = 0
        defaulter_count = 0
        efficiency = 100
        branch_stats = []
        
    context = {
        'late_payments': late_payments,
        'recent_payments': recent_payments,
        'total_late': total_late,
        'total_collected': total_collected,
        'defaulter_count': defaulter_count,
        'efficiency': round(efficiency, 1),
        'branch_stats': branch_stats,
    }
    return render(request, 'reports.html', context)

@login_required
@user_passes_test(lambda u: u.is_admin_or_higher())
def user_list(request):
    if request.user.is_superadmin():
        # Super Admin sees everyone
        users = User.objects.all().order_by('-date_joined')
    else:
        # Regular Admin only sees Customers
        users = User.objects.filter(role='CUSTOMER').order_by('-date_joined')
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_admin_or_higher())
def user_detail(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/user_detail.html', {'target_user': target_user})

@login_required
@user_passes_test(lambda u: u.is_admin_or_higher())
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Create'})

@login_required
@user_passes_test(lambda u: u.is_admin_or_higher())
def user_edit(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=target_user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{target_user.username}" updated successfully.')
            return redirect('user_list')
    else:
        form = CustomUserChangeForm(instance=target_user)
    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Edit', 'target_user': target_user})

@login_required
@user_passes_test(lambda u: u.is_admin_or_higher())
def user_toggle_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        user.is_active = not user.is_active
        user.save()
        messages.success(request, f'User status updated for {user.username}.')
    return redirect('user_list')

@login_required
@user_passes_test(lambda u: u.is_admin_or_higher())
def user_delete(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if target_user != request.user:
        username = target_user.username
        target_user.delete()
        messages.success(request, f'User account "{username}" has been permanently deleted.')
    else:
        messages.error(request, "You cannot delete your own account.")
    return redirect('user_list')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile_view')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'user': request.user, 'form': form})

@login_required
def my_chits_view(request):
    # Only for customers
    if request.user.role != 'CUSTOMER' or not hasattr(request.user, 'member_profile'):
        messages.error(request, 'This view is only available for active Customer accounts.')
        return redirect('dashboard')
    
    from payments.models import Payment
    from django.db.models import Sum
    member = request.user.member_profile
    my_chits_raw = member.chitmember_set.all()
    
    # Enrich with financial data
    my_chits = []
    for mc in my_chits_raw:
        group = mc.chit_group
        total_paid = Payment.objects.filter(
            member=member, 
            chit_group=group, 
            status='PAID'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Calculate Remaining Balance Based on Duration
        # Formula: (Installment Amount * Duration) - Paid Amount
        total_commitment = group.installment_amount * group.duration_months
        remaining_balance = total_commitment - total_paid
        
        # Add to object
        mc.total_paid_in_group = total_paid
        mc.remaining_balance = remaining_balance
        my_chits.append(mc)
        
    return render(request, 'accounts/customer/my_chits.html', {'my_chits': my_chits})

@login_required
def customer_payment_history_view(request):
    # Only for customers
    if request.user.role != 'CUSTOMER' or not hasattr(request.user, 'member_profile'):
        messages.error(request, 'This view is only available for active Customer accounts.')
        return redirect('dashboard')
    
    from payments.models import Payment
    member = request.user.member_profile
    payments = Payment.objects.filter(member=member).order_by('-payment_date')
    return render(request, 'accounts/customer/payment_history.html', {'payments': payments})


@login_required
def update_preferences_view(request):
    import json
    from django.http import JsonResponse
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            
            # Update Boolean preferences
            if 'email_notifications' in data: user.email_notifications = data['email_notifications']
            if 'payment_reminders' in data: user.payment_reminders = data['payment_reminders']
            if 'auction_alerts' in data: user.auction_alerts = data['auction_alerts']
            
            # Update Select preferences
            if 'language' in data: user.language = data['language']
            
            user.save()
            return JsonResponse({'status': 'success', 'message': 'Preferences saved instantly.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

def subscribe_newsletter(request):
    from .models import NewsletterSubscription
    from notifications.models import Notification
    from django.http import JsonResponse
    
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required.'})
            
        if NewsletterSubscription.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'This email is already subscribed.'})
        
        try:
            # Save subscription
            NewsletterSubscription.objects.create(email=email)
            
            # Notify Super Admins
            superadmins = User.objects.filter(role='SUPERADMIN')
            for admin in superadmins:
                Notification.objects.create(
                    user=admin,
                    title="New Newsletter Subscriber",
                    message=f"Someone just joined the newsletter with email: {email}",
                    priority='info'
                )
            
            return JsonResponse({'status': 'success', 'message': 'Thank you for joining our newsletter!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Something went wrong. Please try again later.'})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)

@login_required
def enable_2fa_view(request):
    try:
        import pyotp
    except ImportError:
        messages.error(request, 'The "pyotp" library is not installed in the environment. Please run "pip install pyotp qrcode" first.')
        return redirect('system_settings_view')

    if request.user.two_factor_enabled:
        messages.info(request, 'Two-Factor Authentication is already enabled.')
        return redirect('system_settings_view')

    # Generate a secret key if it doesn't already exist
    if not request.user.two_factor_secret:
        request.user.two_factor_secret = pyotp.random_base32()
        request.user.save()

    # Generate the provisioning URI for the QR code
    totp = pyotp.TOTP(request.user.two_factor_secret)
    provisioning_uri = totp.provisioning_uri(
        name=request.user.email,
        issuer_name="SmartChit Management"
    )

    return render(request, 'accounts/2fa/enable.html', {
        'secret': request.user.two_factor_secret,
        'provisioning_uri': provisioning_uri
    })

@login_required
def verify_2fa_view(request):
    if request.method == 'POST':
        try:
            import pyotp
            otp_token = request.POST.get('otp_token')
            totp = pyotp.TOTP(request.user.two_factor_secret)
            
            if totp.verify(otp_token):
                request.user.two_factor_enabled = True
                request.user.save()
                messages.success(request, 'Two-Factor Authentication has been successfully enabled!')
                return redirect('system_settings_view')
            else:
                messages.error(request, 'Invalid verification code. Please try again.')
        except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')

    return redirect('enable_2fa')

def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            # Generate 6-digit OTP
            otp = ''.join(random.choices(string.digits, k=6))
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()

            # Send Email
            subject = 'Password Reset OTP - SmartChit'
            message = f'Your OTP for resetting your password is: {otp}\n\nThis OTP is valid for 10 minutes.'
            from_email = 'anantha130404@gmail.com'
            send_mail(subject, message, from_email, [email])

            # Redirect to OTP verification page
            request.session['reset_email'] = email
            messages.success(request, 'An OTP has been sent to your email.')
            return redirect('otp_verify')
        else:
            messages.error(request, 'No user found with this email.')
    return render(request, 'accounts/password/password_reset_form.html')

def otp_verify_view(request):
    if 'reset_email' not in request.session:
        return redirect('password_reset')
    
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        email = request.session['reset_email']
        user = User.objects.filter(email=email, otp=otp_entered).first()

        if user:
            # Check if OTP is within 10 minutes
            time_diff = timezone.now() - user.otp_created_at
            if time_diff.total_seconds() < 600: # 10 mins
                request.session['otp_verified'] = True
                messages.success(request, 'OTP verified successfully. Now set your new password.')
                return redirect('password_reset_confirm')
            else:
                messages.error(request, 'OTP has expired. Please request a new one.')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            
    return render(request, 'accounts/password/otp_verify.html')

def password_reset_confirm_view(request):
    if not request.session.get('otp_verified'):
        return redirect('password_reset')

    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            email = request.session['reset_email']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.otp = None # Clear OTP
            user.otp_created_at = None
            user.save()
            
            # Clear session
            del request.session['reset_email']
            del request.session['otp_verified']
            
            messages.success(request, 'Your password has been reset successfully. Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')

    return render(request, 'accounts/password/password_reset_confirm.html')
