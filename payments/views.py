from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django import forms
from django.db.models import Sum, Q, F
from .models import Payment, PaymentProof, PaymentQR
from chits.models import ChitGroup
from members.models import Member
from loans.models import EMISchedule  # Import for total debt check
from notifications.utils import send_payment_receipt_email

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['chit_group', 'member', 'installment_number', 'amount', 'payment_date', 'status']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = PaymentProof
        fields = ['member_name', 'phone_no', 'transaction_id', 'screenshot']
        widgets = {
            'member_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'phone_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Transaction ID'}),
            'screenshot': forms.FileInput(attrs={'class': 'form-control'}),
        }

@login_required
def payment_list(request):
    # Fetch Chit Payments
    chit_payments = Payment.objects.all().select_related('chit_group', 'member', 'collected_by').order_by('-created_at')
    
    # Fetch Loan Payments
    from loan_payments.models import LoanPayment
    loan_payments = LoanPayment.objects.all().select_related('loan__customer', 'collected_by', 'loan__branch').order_by('-created_at')
    
    # Summary Statistics
    from django.db.models import Sum, F
    from django.utils import timezone
    today = timezone.now().date()
    
    # Chit Stats
    chit_total = chit_payments.filter(status='PAID').aggregate(total=Sum(F('amount') + F('penalty_amount')))['total'] or 0
    chit_today = chit_payments.filter(status='PAID', payment_date=today).aggregate(total=Sum(F('amount') + F('penalty_amount')))['total'] or 0
    chit_pending = chit_payments.filter(status__in=['PENDING', 'LATE']).aggregate(total=Sum(F('amount') + F('penalty_amount')))['total'] or 0
    
    # Loan Stats
    loan_total = loan_payments.aggregate(total=Sum(F('amount_paid') + F('penalty_paid')))['total'] or 0
    loan_today = loan_payments.filter(payment_date=today).aggregate(total=Sum(F('amount_paid') + F('penalty_paid')))['total'] or 0
    
    # Calculate Loan Pending (from EMISchedule)
    from loans.models import EMISchedule
    loan_pending = EMISchedule.objects.filter(status__in=['pending', 'overdue']).aggregate(total=Sum(F('emi_amount') + F('penalty_amount')))['total'] or 0
    
    # Calculate System Health (Recovery Rate)
    total_expected = (chit_total + loan_total) + (chit_pending + loan_pending)
    recovery_rate = ((chit_total + loan_total) / total_expected * 100) if total_expected > 0 else 100
    
    context = {
        'chit_payments': chit_payments,
        'loan_payments': loan_payments,
        'total_collected': chit_total + loan_total,
        'today_collected': chit_today + loan_today,
        'total_pending': chit_pending + loan_pending,
        'chit_pending_count': chit_payments.filter(status__in=['PENDING', 'LATE']).count(),
        'loan_pending_count': EMISchedule.objects.filter(status__in=['pending', 'overdue']).count(),
        'recovery_rate': recovery_rate,
    }
    return render(request, 'payments/payment_list.html', context)

@login_required
def payment_create(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            try:
                payment = form.save()
                send_payment_receipt_email(payment)
                messages.success(request, 'Payment recorded successfully. A receipt has been sent to the member\'s email.')
                return redirect('payment_list')
            except Exception as e:
                messages.error(request, 'Payment for this installment already exists or is invalid.')
    else:
        form = PaymentForm()
        
    return render(request, 'payments/payment_form.html', {'form': form, 'title': 'Record Payment'})

@login_required
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment updated successfully.')
            return redirect('payment_list')
    else:
        form = PaymentForm(instance=payment)
        
    return render(request, 'payments/payment_form.html', {'form': form, 'title': 'Edit Payment'})

@login_required
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment deleted successfully.')
        return redirect('payment_list')
    return render(request, 'payments/payment_confirm_delete.html', {'payment': payment})

@login_required
def payment_receipt(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    return render(request, 'payments/payment_receipt_print.html', {'payment': payment})

@login_required
def bulk_reminder_view(request):
    from notifications.utils import send_payment_reminder
    from django.utils import timezone
    import datetime
    
    if not request.user.is_admin_or_higher():
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
        
    today = timezone.now().date()
    target_span = today + datetime.timedelta(days=3)
    pending = Payment.objects.filter(status__in=['PENDING', 'LATE'], due_date__lte=target_span)
    
    sent = 0
    for payment in pending:
        if send_payment_reminder(payment):
            sent += 1
            
    messages.success(request, f"Successfully sent digital reminders to {sent} members.")
    return redirect('payment_list')

from django.db.models import Q, Sum, F, Max
from decimal import Decimal
from django.utils import timezone
from django.http import JsonResponse

@login_required
def get_payment_prediction(request):
    """AJAX endpoint to predict next installment and amount"""
    chit_group_id = request.GET.get('chit_group')
    member_id = request.GET.get('member')
    
    if not chit_group_id or not member_id:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
        
    try:
        group = ChitGroup.objects.get(id=chit_group_id)
        # Get last installment number
        last_inst = Payment.objects.filter(chit_group_id=chit_group_id, member_id=member_id).aggregate(Max('installment_number'))['installment_number__max'] or 0
        next_inst = last_inst + 1
        
        return JsonResponse({
            'installment_number': next_inst,
            'amount': float(group.installment_amount),
            'date': timezone.now().strftime('%Y-%m-%d')
        })
    except ChitGroup.DoesNotExist:
        return JsonResponse({'error': 'Group not found'}, status=404)

@login_required
def staff_collection_report_view(request):
    """Personal collection summary for field staff to tally their daily cash and see monthly progress"""
    if not request.user.is_staff_or_higher():
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
        
    from system_settings.models import SystemSetting
    
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Today's Collections
    my_collections = Payment.objects.filter(
        collected_by=request.user,
        payment_date=today,
        status='PAID'
    ).select_related('member', 'chit_group').order_by('-created_at')
    
    # Today's Total
    daily_total = my_collections.aggregate(
        total=Sum(F('amount') + F('penalty_amount'))
    )['total'] or 0
    
    # Calculate Expected Deposit by subtracting processed handovers
    from payments.models import CashHandover
    approved_handovers = CashHandover.objects.filter(staff=request.user, date=today, status='APPROVED').aggregate(total=Sum('amount'))['total'] or 0
    pending_handovers = CashHandover.objects.filter(staff=request.user, date=today, status='PENDING').aggregate(total=Sum('amount'))['total'] or 0
    
    expected_deposit = Decimal(daily_total) - Decimal(approved_handovers) - Decimal(pending_handovers)
    if expected_deposit < 0: expected_deposit = 0
    
    # Target Logic
    target_str = SystemSetting.get_setting('DAILY_COLLECTION_TARGET', '15000')
    daily_target = Decimal(target_str)
    daily_percentage = min(int((daily_total / daily_target) * 100), 100) if daily_target > 0 else 100
    
    # Monthly Progress
    monthly_collection = Payment.objects.filter(
        collected_by=request.user,
        payment_date__gte=month_start,
        payment_date__lte=today,
        status='PAID'
    )
    
    monthly_total = monthly_collection.aggregate(
        total=Sum(F('amount') + F('penalty_amount'))
    )['total'] or 0
    
    monthly_count = monthly_collection.count()
    
    # Monthly Gamification Engine
    monthly_target_str = SystemSetting.get_setting('MONTHLY_COLLECTION_TARGET', '200000')
    monthly_target = Decimal(monthly_target_str)
    monthly_percentage = min(int((monthly_total / monthly_target) * 100), 100) if monthly_target > 0 else 100
    
    # Incentive Logic (0.5% base + Flat Bonus for 80%+)
    incentive = (Decimal(monthly_total) * Decimal('0.005'))
    if monthly_percentage >= 80:
        incentive += Decimal('1000.0')

    # FOLLOW-UP LIST (CALLER ID)
    # Get all members with LATE or overdue PENDING payments
    late_payments = Payment.objects.filter(
        Q(status='LATE') | Q(status='PENDING', due_date__lt=today)
    ).select_related('member', 'chit_group').order_by('due_date')

    # Group by member to avoid duplicate calls for multiple chits
    follow_up_data = {}
    for p in late_payments:
        if p.member_id not in follow_up_data:
            follow_up_data[p.member_id] = {
                'member': p.member,
                'total_due': 0,
                'chits': [],
                'oldest_due': p.due_date
            }
        follow_up_data[p.member_id]['total_due'] += p.net_amount
        follow_up_data[p.member_id]['chits'].append(p.chit_group.name)

    return render(request, 'payments/staff_report.html', {
        'collections': my_collections,
        'daily_total': daily_total,
        'expected_deposit': expected_deposit,
        'daily_target': daily_target,
        'daily_percentage': daily_percentage,
        'monthly_total': monthly_total,
        'monthly_count': monthly_count,
        'monthly_target': monthly_target,
        'monthly_percentage': monthly_percentage,
        'incentive': incentive,
        'follow_ups': follow_up_data.values(),
        'today': today,
        'title': 'My Workspace'
    })

@login_required
def field_collection_view(request):
    """Simplified, mobile-optimized payment entry for field staff"""
    search_query = request.GET.get('q', '')
    selected_member_id = request.GET.get('member_id')
    
    selected_member = None
    pending_payments = []
    
    if not request.user.is_staff_or_higher():
        messages.error(request, "Access denied. Only staff can use field collection.")
        return redirect('dashboard')
    
    # 1. Handle Payment Submission
    if request.method == 'POST' and 'payment_id' in request.POST:
        payment_id = request.POST.get('payment_id')
        payment = get_object_or_404(Payment, id=payment_id)
        
        payment.status = 'PAID'
        payment.payment_date = timezone.now().date()
        payment.collected_by = request.user
        payment.save()
        
        # Trigger Email Receipt
        send_payment_receipt_email(payment)
        
        import urllib.parse
        
        wa_text = f"Hello {payment.member.name},\n\nYour recent installment for {payment.chit_group.name} (Inst #{payment.installment_number}) of Rs. {payment.net_amount:.0f} has been collected successfully by our executive {request.user.get_full_name() or request.user.username}.\n\nThank you for your prompt payment!"
        wa_link = f"https://wa.me/91{payment.member.phone}?text={urllib.parse.quote(wa_text)}"
        
        btn_html = f"<div class='mt-3 mb-1'><a href='{wa_link}' target='_blank' class='btn btn-sm text-white rounded-pill px-3 shadow-sm flex-fill' style='background-color:#25D366; text-decoration:none;'><i class='bi bi-whatsapp'></i> Send WhatsApp Receipt</a></div>"
        
        from django.utils.safestring import mark_safe
        messages.success(request, mark_safe(
            f"<strong>Collection Recorded!</strong><br>₹{payment.net_amount:.0f} received safely from {payment.member.name}." + btn_html
        ))
        
        return redirect(f"{request.path}?member_id={payment.member.id}")

    # 2. Search Logic
    members = []
    if search_query:
        members_list = Member.objects.filter(
            Q(name__icontains=search_query) | Q(phone__icontains=search_query)
        )[:5].prefetch_related('chit_groups')

        for m in members_list:
            # Financial Snapshot
            m.total_paid = Payment.objects.filter(member=m, status='PAID').aggregate(
                total=Sum(F('amount') + F('penalty_amount'))
            )['total'] or 0
            
            m.total_balance = Payment.objects.filter(member=m, status__in=['PENDING', 'LATE']).aggregate(
                total=Sum(F('amount') + F('penalty_amount'))
            )['total'] or 0
            
            # Chit Progress
            active_chits = m.chit_groups.filter(status='ACTIVE')
            m.total_chit_value = active_chits.aggregate(total=Sum('amount'))['total'] or 0
            m.active_chit_count = active_chits.count()

            # When is their next payment due (oldest pending/late date)
            next_p = Payment.objects.filter(member=m, status__in=['PENDING', 'LATE']).order_by('due_date').first()
            m.next_due = next_p.due_date if next_p else None
            m.next_amount = next_p.net_amount if next_p else 0
            
            members.append(m)

    # 3. Load member details if selected
    if selected_member_id:
        selected_member = get_object_or_404(Member, id=selected_member_id)
        pending_payments = Payment.objects.filter(
            member=selected_member, 
            status__in=['PENDING', 'LATE']
        ).order_by('due_date', 'installment_number')
        
        # Calculate overall balance and next due date for the selected member
        selected_member.total_balance = pending_payments.aggregate(
            total=Sum(F('amount') + F('penalty_amount'))
        )['total'] or 0
        
        selected_member.total_paid = Payment.objects.filter(member=selected_member, status='PAID').aggregate(
            total=Sum(F('amount') + F('penalty_amount'))
        )['total'] or 0
        
        active_chits = selected_member.chit_groups.filter(status='ACTIVE')
        selected_member.total_chit_value = active_chits.aggregate(total=Sum('amount'))['total'] or 0
        
        next_p = pending_payments.first()
        if next_p:
            selected_member.next_due = next_p.due_date
            selected_member.next_amount = next_p.net_amount
        else:
            # Predict future due date for 'Up to date' members
            last_p = Payment.objects.filter(member=selected_member, status='PAID').order_by('-due_date').first()
            if last_p:
                import datetime
                # Standard month logic: handles Year wrap correctly
                # Fallback to payment_date if due_date is null
                d = last_p.due_date or last_p.payment_date or datetime.date.today()
                
                new_year = d.year + (d.month // 12)
                new_month = (d.month % 12) + 1
                if new_month > 12:
                    new_month = 1
                    new_year += 1
                
                try:
                    selected_member.next_due = d.replace(year=new_year, month=new_month)
                except ValueError:
                    # If day is 31 and next month doesn't have it (e.g. Feb)
                    selected_member.next_due = d + datetime.timedelta(days=30)
                    
                selected_member.next_amount = last_p.amount # Use base installment amount
            else:
                # No history and no dues? Default to chit start group if possible
                first_chit = active_chits.first()
                if first_chit:
                    selected_member.next_due = first_chit.start_date
                    selected_member.next_amount = first_chit.installment_amount

    # 4. Today's Summary for display
    today_total = Payment.objects.filter(
        collected_by=request.user,
        payment_date=timezone.now().date(),
        status='PAID'
    ).aggregate(total=Sum(F('amount') + F('penalty_amount')))['total'] or 0

    # 5. Bring in CRM Follow-ups for Today
    from payments.models import FollowUp
    today_follow_ups = FollowUp.objects.filter(
        staff=request.user, 
        reminder_date__lte=timezone.now().date(),
        is_completed=False
    ).select_related('member').order_by('reminder_date')

    return render(request, 'payments/field_collection.html', {
        'members': members,
        'search_query': search_query,
        'selected_member': selected_member,
        'pending_payments': pending_payments,
        'today_total': today_total,
        'today_follow_ups': today_follow_ups,
        'title': 'Field Collection'
    })

@login_required
def initiate_handover(request):
    """
    Handles the EOD Cash Handover request from field staff.
    Calculates today's total cash collected by the staff and sends an approval notification
    to all Super Admins in the network.
    """
    if request.method == 'POST':
        if not request.user.is_staff_or_higher():
            messages.error(request, "Permission denied.")
            return redirect('dashboard')

        from accounts.models import User
        from notifications.models import Notification
        from payments.models import CashHandover

        today = timezone.now().date()
        daily_total = Payment.objects.filter(
            collected_by=request.user,
            payment_date=today,
            status='PAID'
        ).aggregate(
            total=Sum(F('amount') + F('penalty_amount'))
        )['total'] or 0

        approved_handovers = CashHandover.objects.filter(staff=request.user, date=today, status='APPROVED').aggregate(total=Sum('amount'))['total'] or 0
        pending_handovers = CashHandover.objects.filter(staff=request.user, date=today, status='PENDING').aggregate(total=Sum('amount'))['total'] or 0
        
        expected_deposit = Decimal(daily_total) - Decimal(approved_handovers) - Decimal(pending_handovers)

        if expected_deposit <= 0:
            if pending_handovers > 0:
                messages.warning(request, "Your previous cash handover is still pending approval. Please wait for the Branch Manager.")
            else:
                messages.warning(request, "No active cash collected today to hand over.")
            return redirect('staff_report')
            
        # Create the handover record
        handover = CashHandover.objects.create(
            staff=request.user,
            amount=expected_deposit,
            status='PENDING'
        )
        
        # Fire alerts to management
        super_admins = User.objects.filter(role='SUPERADMIN')
        staff_name = request.user.get_full_name() or request.user.username
        
        for admin in super_admins:
            Notification.objects.create(
                user=admin,
                title="Pending Cash Handover",
                message=f"Staff '{staff_name}' requested handover for ₹{expected_deposit}. Please review Branch Handovers panel.",
                priority='warning'
            )
            
        messages.success(request, f"Handover Request securely locked. A notification for ₹{expected_deposit} has been sent to Branch Managers for approval.")
        
    return redirect('staff_report')

@login_required
def handover_list_view(request):
    """
    SuperAdmin/Admin dashboard to view all pending EOD cash handovers.
    """
    if request.user.role not in ['SUPERADMIN', 'ADMIN']:
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
        
    from payments.models import CashHandover
    handovers = CashHandover.objects.all().order_by('-created_at')
    
    return render(request, 'payments/handover_list.html', {
        'handovers': handovers,
        'title': 'Cash Handovers'
    })

@login_required
def approve_handover_view(request, pk):
    if request.user.role not in ['SUPERADMIN', 'ADMIN']:
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
        
    from payments.models import CashHandover
    from notifications.models import Notification
    
    try:
        handover = CashHandover.objects.get(pk=pk, status='PENDING')
        handover.status = 'APPROVED'
        handover.save()
        
        # Notify the staff
        Notification.objects.create(
            user=handover.staff,
            title="Handover Approved",
            message=f"Your cash handover of ₹{handover.amount} on {handover.date.strftime('%b %d')} has been verified & approved by {request.user.username}.",
            priority='success'
        )
        messages.success(request, f"Handover of ₹{handover.amount} from {handover.staff.username} Approved.")
    except CashHandover.DoesNotExist:
        messages.error(request, "Pending handover request not found.")
        
    return redirect('handover_list')

@login_required
def reject_handover_view(request, pk):
    if request.user.role not in ['SUPERADMIN', 'ADMIN']:
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
        
    from payments.models import CashHandover
    from notifications.models import Notification
    
    try:
        handover = CashHandover.objects.get(pk=pk, status='PENDING')
        handover.status = 'REJECTED'
        handover.save()
        
        # Notify the staff
        Notification.objects.create(
            user=handover.staff,
            title="Handover Rejected",
            message=f"Your cash handover of ₹{handover.amount} on {handover.date.strftime('%b %d')} was REJECTED by {request.user.username}. Please contact branch.",
            priority='danger'
        )
        messages.warning(request, f"Handover from {handover.staff.username} has been Rejected.")
    except CashHandover.DoesNotExist:
        messages.error(request, "Pending handover request not found.")
        
    return redirect('handover_list')

@login_required
def add_follow_up(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        note = request.POST.get('note')
        reminder_date = request.POST.get('reminder_date')
        
        if member_id and note and reminder_date:
            from payments.models import FollowUp
            from members.models import Member
            member = get_object_or_404(Member, id=member_id)
            FollowUp.objects.create(
                member=member,
                staff=request.user,
                note=note,
                reminder_date=reminder_date
            )
            messages.success(request, "Follow-up reminder set securely.")
        else:
            messages.error(request, "Please provide valid notes and date.")
            
    return redirect(request.META.get('HTTP_REFERER', 'field_collection'))

@login_required
def complete_follow_up(request, pk):
    from payments.models import FollowUp
    try:
        fu = FollowUp.objects.get(pk=pk, staff=request.user)
        fu.is_completed = True
        fu.save()
        messages.success(request, "Follow-up marked as completed.")
    except FollowUp.DoesNotExist:
        messages.error(request, "Follow-up trace not found.")
    return redirect(request.META.get('HTTP_REFERER', 'field_collection'))

@login_required
def customer_submit_proof(request, payment_id):
    """Customer-facing view to submit digital payment evidence"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Security: Ensure common user can only see their own payment
    if request.user.role == 'CUSTOMER' and hasattr(request.user, 'member_profile'):
        if payment.member != request.user.member_profile:
            messages.error(request, "Permission denied.")
            return redirect('dashboard')

    if request.method == 'POST':
        form = PaymentProofForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if a proof already exists for this payment (handle OneToOne constraint)
            try:
                proof = PaymentProof.objects.get(payment=payment)
                # Update existing proof
                form = PaymentProofForm(request.POST, request.FILES, instance=proof)
                proof = form.save(commit=False)
            except PaymentProof.DoesNotExist:
                proof = form.save(commit=False)
                proof.payment = payment
            
            proof.status = 'PENDING'
            proof.save()
            
            # Update Payment status
            payment.status = 'AWAITING_VERIFICATION'
            payment.save()
            
            # Notify management
            from accounts.models import User
            from notifications.models import Notification
            admins = User.objects.filter(role__in=['SUPERADMIN', 'ADMIN'])
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title="New Payment Evidence",
                    message=f"Proof submitted for {payment.member.name} (₹{payment.amount}). Review required.",
                    priority='info'
                )
            
            messages.success(request, "Payment proof submitted successfully! Our team will verify it shortly.")
            return redirect('dashboard')
    else:
        # Pre-fill if possible
        initial_data = {}
        if hasattr(request.user, 'member_profile'):
            initial_data = {
                'member_name': request.user.member_profile.name,
                'phone_no': request.user.member_profile.phone
            }
        form = PaymentProofForm(initial=initial_data)

    # ── CALCULATE TOTAL DUES (Loan + Chit) ──────────
    from django.utils import timezone
    today = timezone.now().date()
    member = payment.member
    
    # 1. Overdue Chit Dues (excluding current payment if it's already overdue)
    chit_overdue = Payment.objects.filter(
        member=member,
        status__in=['PENDING', 'LATE'],
        due_date__lt=today
    ).exclude(pk=payment.pk).aggregate(
        total=Sum(F('amount') - F('dividend_amount') + F('penalty_amount'))
    )['total'] or 0
    
    # 2. Overdue Loan Dues
    loan_overdue = EMISchedule.objects.filter(
        loan__customer=member,
        status__in=['pending', 'overdue', 'partial'],
        due_date__lt=today
    ).aggregate(
        total=Sum(F('emi_amount') + F('penalty_amount') - F('paid_amount'))
    )['total'] or 0

    total_payable = payment.net_amount + chit_overdue + loan_overdue

    # Fetch the active QR code
    active_qr = PaymentQR.objects.filter(is_active=True).first()
    qr_code_url = active_qr.qr_code.url if active_qr else None

    return render(request, 'payments/customer_submit_proof.html', {
        'form': form,
        'payment': payment,
        'qr_code_url': qr_code_url,
        'chit_overdue': chit_overdue,
        'loan_overdue': loan_overdue,
        'total_payable': total_payable,
    })

@login_required
def admin_proof_list(request):
    """Admin view to see all pending payment verifications"""
    if not request.user.is_admin_or_higher():
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
        
    proofs = PaymentProof.objects.all().select_related('payment__member', 'payment__chit_group').order_by('-submitted_at')
    return render(request, 'payments/admin_proof_list.html', {'proofs': proofs})

@login_required
def admin_process_proof(request, pk, action):
    """Action for Admin to Approve or Reject a payment proof"""
    if not request.user.is_admin_or_higher():
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
        
    proof = get_object_or_404(PaymentProof, pk=pk)
    payment = proof.payment
    
    from notifications.models import Notification
    
    if action == 'approve':
        # Finalize the payment
        proof.status = 'APPROVED'
        proof.processed_at = timezone.now()
        proof.processed_by = request.user
        proof.save()
        
        payment.status = 'PAID'
        payment.payment_date = timezone.now().date()
        payment.collected_by = request.user
        payment.save()
        
        # Trigger Email Receipt
        send_payment_receipt_email(payment)
        
        # Notify Customer
        Notification.objects.create(
            user=payment.member.user,
            title="Payment Verified",
            message=f"Good news! Your payment of ₹{payment.amount} for {payment.chit_group.name} has been verified and approved.",
            priority='success'
        )
        messages.success(request, f"Payment proof for {payment.member.name} APPROVED and payment recorded.")
        
    elif action == 'reject':
        proof.status = 'REJECTED'
        proof.processed_at = timezone.now()
        proof.processed_by = request.user
        reason = request.POST.get('admin_notes', 'Invalid transaction details or screenshot.')
        proof.admin_notes = reason
        proof.save()
        
        # Revert payment status
        payment.status = 'PENDING'
        payment.save()
        
        # Notify Customer
        Notification.objects.create(
            user=payment.member.user,
            title="Payment Rejected",
            message=f"Your payment proof was rejected. Reason: {reason}. Please contact support.",
            priority='danger'
        )
        messages.warning(request, f"Payment proof for {payment.member.name} REJECTED.")
        
    return redirect('admin_proof_list')

@login_required
@user_passes_test(lambda u: u.role in ['ADMIN', 'SUPERADMIN'])
def manage_payment_qr(request):
    from .models import PaymentQR
    if request.method == 'POST':
        if 'delete' in request.POST:
            PaymentQR.objects.filter(id=request.POST.get('qr_id')).delete()
            messages.success(request, "QR Code removed.")
        else:
            qr_file = request.FILES.get('qr_code')
            if qr_file:
                # Deactivate others if this one is active
                PaymentQR.objects.all().update(is_active=False)
                PaymentQR.objects.create(qr_code=qr_file, is_active=True)
                messages.success(request, "New Payment QR uploaded and activated.")
        return redirect('manage_payment_qr')

    qrs = PaymentQR.objects.all().order_by('-created_at')
    return render(request, 'payments/manage_qr.html', {'qrs': qrs})
