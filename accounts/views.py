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
    from payments.utils import update_penalties # NEW IMPORT
    from django.db.models import Sum, Count
    from django.utils import timezone
    import datetime
    
    # Automaticaly check and apply penalties
    try:
        update_penalties()
    except Exception as e:
        print(f"DEBUG: Penalty update skipped due to: {e}")

    # Imports for Unification
    from loans.models import Loan, EMISchedule
    from loan_payments.models import LoanPayment
    from datetime import date, timedelta

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    today_notifications_count = Notification.objects.filter(user=request.user, is_read=False, created_at__gte=today_start).count()

    # LOAN AGENT — STAFF user with a linked LoanAgent profile
    if request.user.role in ['STAFF', 'ADMIN', 'SUPERADMIN'] and hasattr(request.user, 'loan_agent_profile'):
        # If they are purely an agent (STAFF), redirect to agent dashboard
        if request.user.role == 'STAFF':
            return redirect('loan_agent_dashboard')

    # LOAN CUSTOMER — no chit fund member_profile, only loan_customer_profile
    if request.user.role == 'CUSTOMER' and not hasattr(request.user, 'member_profile'):
        if hasattr(request.user, 'loan_customer_profile'):
            return redirect('loan_customer_portal')
        # Fallback: has neither profile — show basic denial
        messages.info(request, "Your account is being set up. Please contact the office.")
        logout(request)
        return redirect('login')

    # CUSTOMER PERSONALIZED DASHBOARD (Chit Fund member)
    if request.user.role == 'CUSTOMER' and hasattr(request.user, 'member_profile'):
        from django.db.models import F
        member = request.user.member_profile
        my_chit_members = ChitMember.objects.filter(member=member).select_related('chit_group')
        my_groups_count = my_chit_members.count()
        
        # Calculate Net Totals: (Gross Amount - Dividend + Penalty)
        total_paid = Payment.objects.filter(member=member, status='PAID').aggregate(
            net_sum=Sum(F('amount') - F('dividend_amount') + F('penalty_amount'))
        )['net_sum'] or 0
        
        total_pending = Payment.objects.filter(member=member, status__in=['PENDING', 'LATE']).aggregate(
            net_sum=Sum(F('amount') - F('dividend_amount') + F('penalty_amount'))
        )['net_sum'] or 0
        
        total_dividend = Payment.objects.filter(member=member).aggregate(Sum('dividend_amount'))['dividend_amount__sum'] or 0
        
        # ACTIVE CHITS List
        upcoming_projection = 0
        active_chits = []
        for mc in my_chit_members:
            if mc.chit_group.status == 'ACTIVE':
                # Use Net Amount for Group aggregation
                paid_in_group = Payment.objects.filter(
                    member=member, 
                    chit_group=mc.chit_group, 
                    status='PAID'
                ).aggregate(
                    net_sum=Sum(F('amount') - F('dividend_amount') + F('penalty_amount'))
                )['net_sum'] or 0
                
                total_inst = mc.chit_group.duration_months
                paid_inst = Payment.objects.filter(member=member, chit_group=mc.chit_group, status='PAID').count()
                percent = (paid_inst / total_inst * 100) if total_inst > 0 else 0
                
                # Projection for "Again Upcoming" if no pending exists
                upcoming_projection += mc.chit_group.installment_amount
                
                # TOTAL CHIT COMMITMENT: (Total Value - Paid So Far)
                total_commitment = mc.chit_group.amount # Value of the chit
                count_paid = Payment.objects.filter(member=member, chit_group=mc.chit_group, status='PAID').count()
                inst_val = mc.chit_group.installment_amount
                # Simpler: Remaining installments * installment_amount
                rem_inst = mc.chit_group.duration_months - count_paid
                
                active_chits.append({
                    'id': mc.id,
                    'group': mc.chit_group,
                    'paid_amount': paid_in_group,
                    'total_installments': total_inst,
                    'paid_installments': paid_inst,
                    'remaining_commitment': rem_inst * inst_val,
                    'percent': round(percent, 1)
                })

        # UPCOMING AUCTIONS Projection (Customer)
        upcoming_auctions_list = []
        for mc in my_chit_members:
            if mc.chit_group.status == 'ACTIVE':
                last_auction = Auction.objects.filter(chit_group=mc.chit_group).order_by('-month_number').first()
                if last_auction:
                    next_month = last_auction.month_number + 1
                    if next_month <= mc.chit_group.duration_months:
                        upcoming_auctions_list.append({
                            'group_name': mc.chit_group.name,
                            'month_number': next_month,
                            'expected_date': last_auction.auction_date + datetime.timedelta(days=30)
                        })
                else:
                    upcoming_auctions_list.append({
                        'group_name': mc.chit_group.name,
                        'month_number': 1,
                        'expected_date': mc.chit_group.start_date
                    })
        
        recent_my_payments = Payment.objects.filter(member=member).order_by('-payment_date')[:5]
        
        relevant_group_ids = my_chit_members.values_list('chit_group_id', flat=True)
        recent_group_auctions = Auction.objects.filter(chit_group_id__in=relevant_group_ids).order_by('-auction_date')[:5]

        # Get Actual Pending Payments for Online Pay feature
        pending_payments_list = Payment.objects.filter(
            member=member, 
            status__in=['PENDING', 'LATE', 'AWAITING_VERIFICATION']
        ).select_related('chit_group').order_by('due_date')

        # Chart Data: Total Contribution vs Total Possible Target
        total_target_value = sum(ac['group'].amount for ac in active_chits)

        # ── LOAN DATA UNIFICATION ─────────────────────
        loans = Loan.objects.filter(customer=member)
        # Include active, approved, pending (applications), and default (unpaid) loans
        active_loans = loans.filter(status__in=['active', 'approved', 'default', 'pending'])
        
        upcoming_emis = EMISchedule.objects.filter(
            loan__customer=member, 
            status='pending',
            due_date__gte=date.today(),
            due_date__lte=date.today() + timedelta(days=30)
        ).select_related('loan').order_by('due_date')

        overdue_emis = EMISchedule.objects.filter(
            loan__customer=member,
            status='overdue'
        ).select_related('loan').order_by('due_date')
        
        total_loan_outstanding = loans.filter(status='active').aggregate(
            s=Sum('outstanding_balance'))['s'] or 0
            
        recent_loan_payments = LoanPayment.objects.filter(
            loan__customer=member
        ).select_related('emi_installment', 'loan').order_by('-payment_date')[:5]

        # Consolidated Financial Stats
        total_chit_rem = sum(ac['remaining_commitment'] for ac in active_chits)
        total_liability = total_chit_rem + total_loan_outstanding

        context = {
            'role': 'CUSTOMER',
            'member': member,
            'my_groups_count': my_groups_count,
            'total_paid': total_paid,
            'total_pending': total_pending, # Chit pending
            'total_dividend': total_dividend,
            'total_target_value': total_target_value,
            'active_chits': active_chits,
            'upcoming_auctions': upcoming_auctions_list,
            'recent_payments': recent_my_payments,
            'pending_payments_list': pending_payments_list,
            'recent_auctions': recent_group_auctions,

            # Unified Loan Context
            'loans': loans,
            'active_loans': active_loans,
            'upcoming_emis': upcoming_emis,
            'overdue_emis': overdue_emis,
            'total_loan_outstanding': total_loan_outstanding,
            'recent_loan_payments': recent_loan_payments,
            'total_liability': total_liability,

            'notifications': notifications,
            'today_notifications_count': today_notifications_count,
            'now': now,
        }
        return render(request, 'accounts/customer/dashboard.html', context)

    # ADMIN / STAFF DASHBOARD (Unified Chit & Loan)
    from payments.models import PaymentProof
    from loan_payments.models import LoanPayment
    from loans.models import Loan, EMISchedule
    from django.db.models import F

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
            
        # ── REVENUE AGGREGATION (Unified) ──────────
        chit_received = Payment.objects.filter(status='PAID').aggregate(Sum('amount'))['amount__sum'] or 0
        loan_received = LoanPayment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        total_received = chit_received + loan_received
        
        # ── LIABILITY AGGREGATION (Unified) ──────────
        chit_pending = Payment.objects.filter(status__in=['PENDING', 'LATE']).aggregate(Sum('amount'))['amount__sum'] or 0
        loan_pending = EMISchedule.objects.filter(status__in=['pending', 'overdue', 'partial'], due_date__lt=now.date()).aggregate(
            total=Sum(F('emi_amount') + F('penalty_amount') - F('paid_amount'))
        )['total'] or 0
        total_pending = chit_pending + loan_pending
        
        # Monthly Collection Trend based on selected period (Unified)
        chart_labels = []
        chart_data = []
        for i in range(months_back - 1, -1, -1):
            target_date = now - datetime.timedelta(days=i*30)
            month_label = target_date.strftime('%b')
            
            # Chit Revenue
            chit_sum = Payment.objects.filter(
                status='PAID', 
                payment_date__year=target_date.year, 
                payment_date__month=target_date.month
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            # Loan Revenue
            loan_sum = LoanPayment.objects.filter(
                payment_date__year=target_date.year, 
                payment_date__month=target_date.month
            ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
            
            chart_labels.append(month_label)
            chart_data.append(float(chit_sum + loan_sum))

        # Branch-wise Member Distribution (Volume Density)
        branch_dist = Branch.objects.annotate(count=Count('members')).values('name', 'count')
        group_labels = [b['name'] for b in branch_dist]
        group_counts = [b['count'] for b in branch_dist]

        # Performance and Periodical Logic (Today's Unified Collection)
        now_date = now.date()
        chit_today = Payment.objects.filter(status='PAID', payment_date__gte=now_date).aggregate(Sum('amount'))['amount__sum'] or 0
        loan_today = LoanPayment.objects.filter(payment_date__gte=now_date).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        daily_collected = chit_today + loan_today
        
        # PROJECTION for Upcoming Auctions (Admin All Groups)
        upcoming_global_auctions = []
        active_groups = ChitGroup.objects.filter(status='ACTIVE')
        for grp in active_groups:
            last_auc = Auction.objects.filter(chit_group=grp).order_by('-month_number').first()
            if last_auc:
                nxt_m = last_auc.month_number + 1
                if nxt_m <= grp.duration_months:
                    upcoming_global_auctions.append({
                        'group_name': grp.name,
                        'month_number': nxt_m,
                        'expected_date': last_auc.auction_date + datetime.timedelta(days=30)
                    })
            else:
                upcoming_global_auctions.append({
                    'group_name': grp.name,
                    'month_number': 1,
                    'expected_date': grp.start_date
                })
        
        # Sort by date
        upcoming_global_auctions = sorted(upcoming_global_auctions, key=lambda x: x['expected_date'])[:5]
        
        # Performance Context
        total_potential = total_received + total_pending
        perf_pct = round((total_received / total_potential) * 100, 1) if total_potential > 0 else 0
        
        context = {
            'role': request.user.role,
            'total_members': Member.objects.count(),
            'total_branches': Branch.objects.count(),
            'total_auctions': Auction.objects.count(),
            'active_chits': active_groups.count(),
            'active_loans': Loan.objects.filter(status='active').count(),
            'total_received': total_received,
            'total_pending': total_pending,
            'daily_collected': daily_collected,
            
            # Recent & Followups
            'recent_payments': Payment.objects.select_related('member').order_by('-payment_date')[:5],
            'followup_list': Payment.objects.filter(status__in=['PENDING', 'LATE']).select_related('member', 'chit_group').order_by('due_date')[:5],
            'upcoming_auctions': upcoming_global_auctions,
            'recent_logs': LogEntry.objects.all().order_by('-timestamp')[:8],
            'pending_verifications_count': PaymentProof.objects.filter(status='PENDING').count(),
            
            # Chart & Filter Info
            'chart_labels': chart_labels,
            'chart_data': chart_data,
            'group_labels': group_labels,
            'group_counts': group_counts,
            'performance_percent': perf_pct,
            'active_period': period,
            'period_label': period_label,
            'notifications': notifications,
            'today_notifications_count': today_notifications_count,
            'now': now,
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
        pending_in_group = Payment.objects.filter(member=member, chit_group=group, status__in=['PENDING', 'LATE']).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Balance = Total Value of Chit - What we have paid
        balance = max(0, group.amount - paid_in_group)
        
        # Next Due Logic (Projected installment if none pending)
        next_due = pending_in_group if pending_in_group > 0 else group.installment_amount
        
        chit_breakdown.append({
            'group_name': group.name,
            'chit_value': group.amount,
            'paid_amount': paid_in_group,
            'balance_amount': balance,
            'upcoming_amount': next_due,
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
def customer_passbook_view(request, mc_id):
    """Generates a detailed digital passbook for a specific chit group (Customer & Admin Access)"""
    from django.shortcuts import get_object_or_404
    from chits.models import ChitMember
    from payments.models import Payment
    from django.db.models import Sum
    
    # Permission Logic: Admin can see any, Customer can only see their own
    if request.user.is_superuser or request.user.role in ['ADMIN', 'BRANCH_MANAGER']:
        mc = get_object_or_404(ChitMember, id=mc_id)
    else:
        mc = get_object_or_404(ChitMember, id=mc_id, member__user=request.user)
        
    group = mc.chit_group
    
    # 2. Fetch all payments for this group (Paid & Pending)
    payments = Payment.objects.filter(member=mc.member, chit_group=group).order_by('installment_number')
    payments_dict = {p.installment_number: p for p in payments}
    
    # 3. Generate Full Schedule (Automatic Payment Projection)
    import datetime
    full_schedule = []
    for i in range(1, group.duration_months + 1):
        if i in payments_dict:
            full_schedule.append(payments_dict[i])
        else:
            # Create a virtual entry for future/upcoming months
            due_date = group.start_date + datetime.timedelta(days=30 * (i-1))
            full_schedule.append({
                'installment_number': i,
                'due_date': due_date,
                'amount': group.installment_amount,
                'dividend_amount': 0,
                'net_amount': group.installment_amount,
                'status': 'UPCOMING',
                'is_virtual': True,
                'dynamic_status': 'UPCOMING' if due_date > datetime.date.today() else 'OVERDUE'
            })

    # 4. Calculate summary metrics for the passbook header
    stats = payments.filter(status='PAID').aggregate(
        total_paid=Sum('amount'), 
        total_dividend=Sum('dividend_amount'),
        total_penalty=Sum('penalty_amount')
    )
    
    # 5. Final context for the passbook layout
    context = {
        'mc': mc,
        'group': group,
        'schedule': full_schedule,
        'summary': {
            'invested': stats['total_paid'] or 0,
            'earned': stats['total_dividend'] or 0,
            'penalties': stats['total_penalty'] or 0,
            'net_outflow': (stats['total_paid'] or 0) - (stats['total_dividend'] or 0) + (stats['total_penalty'] or 0)
        }
    }
    return render(request, 'accounts/customer/passbook.html', context)

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
        from loans.models import Loan, EMISchedule
        from loan_payments.models import LoanPayment
        from django.db.models import Sum, Q
        from django.utils import timezone
        from datetime import timedelta, date
        
        # Base Data
        late_payments = Payment.objects.filter(status='LATE')
        recent_payments = Payment.objects.filter(status='PAID').order_by('-payment_date')[:10]
        
        # Global Aggregates
        total_late = late_payments.aggregate(Sum('amount'))['amount__sum'] or 0
        total_collected = Payment.objects.filter(status='PAID').aggregate(Sum('amount'))['amount__sum'] or 0
        defaulter_count = late_payments.values('member').distinct().count()
        
        # NEW: Time-based Collections
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        daily_collected = Payment.objects.filter(status='PAID', payment_date__gte=today_start.date()).aggregate(Sum('amount'))['amount__sum'] or 0
        weekly_collected = Payment.objects.filter(status='PAID', payment_date__gte=week_start.date()).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_collected = Payment.objects.filter(status='PAID', payment_date__gte=month_start.date()).aggregate(Sum('amount'))['amount__sum'] or 0

        # Efficiency calculation
        total_potential = total_collected + total_late
        efficiency = (total_collected / total_potential * 100) if total_potential > 0 else 100
        
        # --- LOAN AGGREGATES ---
        loan_payments_all = LoanPayment.objects.all()
        overdue_emis = EMISchedule.objects.filter(status='overdue')
        
        loan_total_collected = loan_payments_all.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        loan_total_overdue = overdue_emis.aggregate(Sum('emi_amount'))['emi_amount__sum'] or 0
        
        loan_daily_collected = loan_payments_all.filter(payment_date__gte=today_start.date()).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        loan_weekly_collected = loan_payments_all.filter(payment_date__gte=week_start.date()).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        loan_monthly_collected = loan_payments_all.filter(payment_date__gte=month_start.date()).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        
        loan_potential = float(loan_total_collected) + float(loan_total_overdue)
        loan_efficiency = (float(loan_total_collected) / loan_potential * 100) if loan_potential > 0 else 100

        # Branch Performance (Unified)
        from branches.models import Branch
        from members.models import Member
        branches = Branch.objects.all()
        branch_stats = []
        for branch in branches:
            chit_collected = Payment.objects.filter(member__branch=branch, status='PAID').aggregate(Sum('amount'))['amount__sum'] or 0
            loan_collected = LoanPayment.objects.filter(loan__customer__branch=branch).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
            
            branch_member_count = Member.objects.filter(branch=branch).count()
            branch_stats.append({
                'name': branch.name,
                'chit_collected': chit_collected,
                'loan_collected': loan_collected,
                'total_collected': float(chit_collected) + float(loan_collected),
                'member_count': branch_member_count
            })
            
        # Recent Loan Activity
        recent_loan_payments = LoanPayment.objects.select_related('loan__customer').order_by('-payment_date')[:10]
            
    except Exception as e:
        print(f"DEBUG REPORT ERROR: {e}")
        late_payments = []
        recent_payments = []
        total_late = 0
        total_collected = 0
        daily_collected = 0
        weekly_collected = 0
        monthly_collected = 0
        defaulter_count = 0
        efficiency = 100
        branch_stats = []
        
    context = {
        # Chit Data
        'late_payments': late_payments,
        'recent_payments': recent_payments,
        'total_late': total_late,
        'total_collected': total_collected,
        'daily_collected': daily_collected,
        'weekly_collected': weekly_collected,
        'monthly_collected': monthly_collected,
        'defaulter_count': defaulter_count,
        'efficiency': round(efficiency, 1),
        
        # Loan Data
        'loan_total_collected': loan_total_collected,
        'loan_total_overdue': loan_total_overdue,
        'loan_daily_collected': loan_daily_collected,
        'loan_weekly_collected': loan_weekly_collected,
        'loan_monthly_collected': loan_monthly_collected,
        'loan_efficiency': round(loan_efficiency, 1),
        'recent_loan_payments': recent_loan_payments,
        'overdue_emis_list': overdue_emis[:10],
        
        # Combined/Global
        'branch_stats': branch_stats,
        'grand_total_collected': float(total_collected) + float(loan_total_collected),
        'grand_total_overdue': float(total_late) + float(loan_total_overdue),
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
        
        # Progress Percentage
        percent_complete = (total_paid / total_commitment * 100) if total_commitment > 0 else 0
        
        # Calculate Next Payment Date
        paid_count = Payment.objects.filter(member=member, chit_group=group, status='PAID').count()
        # Next payment is start_date + N months
        # Note: simplistic month increment for logic
        next_date = group.start_date + datetime.timedelta(days=31 * paid_count)
        mc.next_payment_date = next_date
        
        # Add to object
        mc.total_paid_in_group = total_paid
        mc.remaining_balance = remaining_balance
        mc.percent_complete = round(percent_complete, 1)
        my_chits.append(mc)
        
    return render(request, 'accounts/customer/my_chits.html', {
        'my_chits': my_chits,
        'now': timezone.now()
    })

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

@login_required
def customer_pay_view(request):
    """View for Customers to see their pending dues and branch payment instructions"""
    if request.user.role != 'CUSTOMER' or not hasattr(request.user, 'member_profile'):
        messages.error(request, 'Profile not found.')
        return redirect('dashboard')
        
    from payments.models import Payment
    from django.db.models import Sum
    
    member = request.user.member_profile
    pending_payments = Payment.objects.filter(member=member, status__in=['PENDING', 'LATE']).order_by('due_date')
    
    total_due = sum(p.net_amount for p in pending_payments)
    
    return render(request, 'accounts/customer/pay_now.html', {
        'pending_payments': pending_payments,
        'total_due': total_due,
        'member': member,
        'bank_details': {
            'account_name': 'CHIT FUND MANAGEMENT LTD',
            'account_no': '9876543210123',
            'ifsc': 'UTIB0000123',
            'bank_name': 'Axis Bank, Main Branch'
        }
    })

@login_required
def customer_payment_success(request):
    """Callback after successful payment (Demonstration/Simulated)"""
    if request.method == 'POST':
        from payments.models import Payment
        from django.utils import timezone
        
        member = request.user.member_profile
        pending = Payment.objects.filter(member=member, status__in=['PENDING', 'LATE'])
        
        count = 0
        for p in pending:
            p.status = 'PAID'
            p.payment_date = timezone.now().date()
            p.save()
            count += 1
            
        messages.success(request, f'Successfully paid {count} installments. Your account has been updated.')
    return redirect('dashboard')
@login_required
def global_search_api(request):
    from django.http import JsonResponse
    from django.db.models import Q
    from members.models import Member
    from chits.models import ChitGroup
    from auctions.models import Auction
    from django.urls import reverse
    
    query = request.GET.get('q', '').strip()
    results = []
    
    if len(query) >= 2:
        # 1. Search Members (By Name or Phone)
        members = Member.objects.filter(
            Q(name__icontains=query) | Q(phone__icontains=query)
        )[:5]
        for m in members:
            results.append({
                'title': m.name,
                'type': 'Member',
                'url': reverse('member_detail', args=[m.id]),
                'info': f'Phone: {m.phone}'
            })

        # 2. Search Chit Groups (By Name)
        chits = ChitGroup.objects.filter(
            Q(name__icontains=query)
        )[:5]
        for c in chits:
            results.append({
                'title': c.name,
                'type': 'Chit Group',
                'url': reverse('chit_detail', args=[c.id]),
                'info': f'Value: ₹{c.amount}'
            })

        # 3. Search Auctions (By Winner Name)
        auctions = Auction.objects.filter(
            Q(winner__name__icontains=query) | Q(chit_group__name__icontains=query)
        ).select_related('winner', 'chit_group')[:5]
        for a in auctions:
            results.append({
                'title': f'Auction: {a.winner.name}',
                'type': 'Auction Result',
                'url': reverse('auction_detail', args=[a.id]),
                'info': f'Group: {a.chit_group.name}'
            })

        # 4. Search Loans (By Customer Name or Loan ID)
        from loans.models import Loan
        loans = Loan.objects.filter(
            Q(customer__name__icontains=query) | Q(id__icontains=query)
        ).select_related('customer')[:5]
        for l in loans:
            results.append({
                'title': f'Loan #{l.id}: {l.customer.name}',
                'type': 'Loan Record',
                'url': reverse('loan_detail', args=[l.id]),
                'info': f'Amount: ₹{l.loan_amount} ({l.status})'
            })

        # 5. Search Loan Customers (By Name or Phone)
        from loan_customers.models import LoanCustomer
        l_customers = LoanCustomer.objects.filter(
            Q(name__icontains=query) | Q(phone__icontains=query)
        )[:5]
        for lc in l_customers:
            results.append({
                'title': lc.name,
                'type': 'Loan Customer',
                'url': reverse('loan_customer_detail', args=[lc.id]),
                'info': f'Phone: {lc.phone}'
            })

    return JsonResponse({'results': results})
