from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from decimal import Decimal
from .models import Loan, EMISchedule
from .forms import LoanApplicationForm, LoanApprovalForm, TopUpLoanForm
from members.models import Member
from .utils import generate_emi_schedule, recalculate_outstanding


def staff_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings as djsettings
            return redirect(djsettings.LOGIN_URL)
        if request.user.role not in ['SUPERADMIN', 'ADMIN', 'STAFF']:
            messages.error(request, "Access denied.")
            return redirect('loan_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


def admin_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings as djsettings
            return redirect(djsettings.LOGIN_URL)
        if request.user.role not in ['SUPERADMIN', 'ADMIN']:
            messages.error(request, "Admin access required.")
            return redirect('loan_list')
        return view_func(request, *args, **kwargs)
    return _wrapped


# ──────────────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────────────

@login_required
def loan_dashboard(request):
    """
    Role-aware dashboard for the Loan Management module.
    - SUPERADMIN/ADMIN: full portfolio metrics + approval queue + branch breakdown
    - STAFF: branch-scoped metrics + collection focus
    - Agent users: redirect to agent dashboard
    """
    user = request.user

    # Redirect agents to their dedicated dashboard
    if hasattr(user, 'loan_agent_profile'):
        return redirect('loan_agent_dashboard')

    from datetime import date, timedelta
    from loan_payments.models import LoanPayment
    from django.apps import apps
    LoanPaymentProof = apps.get_model('loan_payments', 'LoanPaymentProof')
    from loan_customers.models import LoanAgent
    from branches.models import Branch
    from django.db.models import Count, Sum

    today = date.today()
    is_admin = user.role in ['SUPERADMIN', 'ADMIN']

    # Scope loans/emis based on role
    if is_admin:
        loans_qs = Loan.objects.all()
        emis_qs  = EMISchedule.objects.all()
        payments_qs = LoanPayment.objects.all()
    else:
        # STAFF: show all loans (they collect across branches)
        loans_qs = Loan.objects.all()
        emis_qs  = EMISchedule.objects.all()
        payments_qs = LoanPayment.objects.filter(collected_by=user)

    stats = {
        'total_loans':       loans_qs.count(),
        'active_loans':      loans_qs.filter(status='active').count(),
        'pending_approval':  loans_qs.filter(status='pending').count(),
        'closed_loans':      loans_qs.filter(status='closed').count(),
        'default_loans':     loans_qs.filter(status='default').count(),
        'total_disbursed':   loans_qs.filter(status__in=['active', 'closed']).aggregate(
                                 s=Sum('loan_amount'))['s'] or 0,
        'total_outstanding': loans_qs.filter(status='active').aggregate(
                                 s=Sum('outstanding_balance'))['s'] or 0,
        'total_collected':   emis_qs.filter(status='paid').aggregate(
                                 s=Sum('paid_amount'))['s'] or 0,
        'overdue_emis':      emis_qs.filter(status='overdue').count(),
        'pending_emis':      emis_qs.filter(status='pending').count(),
        'pending_proofs':    LoanPaymentProof.objects.filter(status='PENDING').count(),
        # Today's collection
        'today_collection':  payments_qs.filter(payment_date=today).aggregate(
                                 s=Sum('amount_paid'))['s'] or 0,
        # This month
        'month_collection':  payments_qs.filter(
                                 payment_date__year=today.year,
                                 payment_date__month=today.month
                             ).aggregate(s=Sum('amount_paid'))['s'] or 0,
    }

    # Recent loans
    recent_loans = Loan.objects.select_related('customer', 'branch').order_by('-created_at')[:8]

    # Upcoming EMIs in next 7 days
    upcoming_emis = EMISchedule.objects.filter(
        status='pending',
        due_date__range=[today, today + timedelta(days=7)]
    ).select_related('loan__customer').order_by('due_date')[:10]

    # Pending approvals (admin only)
    pending_loans = []
    if is_admin:
        pending_loans = Loan.objects.filter(status='pending').select_related(
            'customer', 'branch', 'created_by'
        ).order_by('created_at')[:8]

    # Branch-wise breakdown (admin only)
    branch_stats = []
    if is_admin:
        for branch in Branch.objects.all():
            bl = loans_qs.filter(branch=branch)
            branch_stats.append({
                'name':        branch.name,
                'total':       bl.count(),
                'active':      bl.filter(status='active').count(),
                'overdue':     EMISchedule.objects.filter(
                                   loan__branch=branch, status='overdue').count(),
                'outstanding': bl.filter(status='active').aggregate(
                                   s=Sum('outstanding_balance'))['s'] or 0,
            })

    # Overdue follow-up list (staff view)
    overdue_list = EMISchedule.objects.filter(
        status='overdue'
    ).select_related('loan__customer', 'loan__branch').order_by('due_date')[:8]

    return render(request, 'loans/dashboard.html', {
        'stats':         stats,
        'recent_loans':  recent_loans,
        'upcoming_emis': upcoming_emis,
        'pending_loans': pending_loans,
        'branch_stats':  branch_stats,
        'overdue_list':  overdue_list,
        'is_admin':      is_admin,
    })




# ──────────────────────────────────────────────────────
# LOAN LIST & DETAIL
# ──────────────────────────────────────────────────────

@login_required
@staff_required
def loan_list(request):
    qs = Loan.objects.select_related('customer', 'branch').order_by('-created_at')

    # Filters
    status = request.GET.get('status', '')
    q = request.GET.get('q', '')
    branch_id = request.GET.get('branch', '')

    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(
            Q(loan_number__icontains=q) |
            Q(customer__name__icontains=q) |
            Q(customer__phone__icontains=q)
        )
    if branch_id:
        qs = qs.filter(branch_id=branch_id)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    from branches.models import Branch
    return render(request, 'loans/loan_list.html', {
        'page_obj': page_obj,
        'status': status,
        'q': q,
        'branch_id': branch_id,
        'branches': Branch.objects.all(),
        'status_choices': Loan.STATUS_CHOICES,
        'total': qs.count(),
    })


@login_required
@staff_required
def loan_detail(request, pk):
    loan = get_object_or_404(
        Loan.objects.select_related('customer', 'branch', 'approved_by', 'created_by'),
        pk=pk
    )
    emi_schedule = loan.emi_schedule.all()
    payments = loan.loanpayment_set.select_related('collected_by').order_by('-payment_date')

    return render(request, 'loans/loan_detail.html', {
        'loan': loan,
        'emi_schedule': emi_schedule,
        'payments': payments,
    })


@login_required
@staff_required
def loan_create(request):
    """Create a new loan application."""
    customer_pk = request.GET.get('customer')
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST, customer_pk=customer_pk)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.created_by = request.user
            loan.status = 'pending'
            loan.save()
            messages.success(request, f"Loan application {loan.loan_number} created. Awaiting approval.")
            return redirect('loan_detail', pk=loan.pk)
    else:
        form = LoanApplicationForm(customer_pk=customer_pk)

    return render(request, 'loans/loan_form.html', {
        'form': form,
        'title': 'New Loan Application',
    })


# ──────────────────────────────────────────────────────
# APPROVAL WORKFLOW
# ──────────────────────────────────────────────────────

@login_required
@admin_required
def loan_approve(request, pk):
    """Approve or reject a pending loan."""
    loan = get_object_or_404(Loan, pk=pk, status='pending')

    if request.method == 'POST':
        form = LoanApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']

            if action == 'approve':
                loan.approve(request.user)
                # Auto-disburse if disbursement_mode is provided
                mode = form.cleaned_data.get('disbursement_mode', '')
                ref  = form.cleaned_data.get('disbursement_reference', '')
                if mode:
                    loan.disburse(mode=mode, reference=ref)
                messages.success(request, f"Loan {loan.loan_number} approved and disbursed.")

            elif action == 'reject':
                reason = form.cleaned_data.get('rejection_reason', '')
                if not reason:
                    messages.error(request, "Please provide a rejection reason.")
                    return render(request, 'loans/loan_approve.html', {'loan': loan, 'form': form})
                loan.reject(reason)
                messages.warning(request, f"Loan {loan.loan_number} rejected.")

            return redirect('loan_detail', pk=loan.pk)
    else:
        form = LoanApprovalForm()

    return render(request, 'loans/loan_approve.html', {'loan': loan, 'form': form})


@login_required
@admin_required
def loan_disburse(request, pk):
    """Manually disburse an approved (but not yet active) loan."""
    loan = get_object_or_404(Loan, pk=pk, status='approved')
    if request.method == 'POST':
        mode = request.POST.get('mode', 'cash')
        ref  = request.POST.get('reference', '')
        loan.disburse(mode=mode, reference=ref)
        messages.success(request, f"Loan {loan.loan_number} disbursed successfully.")
        return redirect('loan_detail', pk=loan.pk)
    return render(request, 'loans/loan_disburse.html', {'loan': loan})


# ──────────────────────────────────────────────────────
# TOP-UP LOAN
# ──────────────────────────────────────────────────────

@login_required
@staff_required
def loan_topup(request, pk):
    """Create a top-up loan on an existing active loan."""
    parent_loan = get_object_or_404(Loan, pk=pk, status='active')

    if request.method == 'POST':
        form = TopUpLoanForm(request.POST)
        if form.is_valid():
            top_up = form.save(commit=False)
            top_up.customer = parent_loan.customer
            top_up.branch   = parent_loan.branch
            top_up.parent_loan = parent_loan
            top_up.created_by = request.user
            top_up.status = 'pending'
            top_up.save()
            messages.success(request, f"Top-up loan {top_up.loan_number} created. Awaiting approval.")
            return redirect('loan_detail', pk=top_up.pk)
    else:
        form = TopUpLoanForm(initial={
            'interest_rate': parent_loan.interest_rate,
            'interest_type': parent_loan.interest_type,
            'penalty_rate': parent_loan.penalty_rate,
        })

    return render(request, 'loans/loan_topup.html', {
        'form': form,
        'parent_loan': parent_loan,
    })


# ──────────────────────────────────────────────────────
# EMI SCHEDULE
# ──────────────────────────────────────────────────────

@login_required
@staff_required
def loan_emi_schedule(request, pk):
    """Full EMI schedule / amortisation table for a loan."""
    loan = get_object_or_404(Loan.objects.select_related('customer'), pk=pk)
    schedule = loan.emi_schedule.all()
    return render(request, 'loans/emi_schedule.html', {
        'loan': loan,
        'schedule': schedule,
    })


# ──────────────────────────────────────────────────────
# AJAX: EMI CALCULATOR
# ──────────────────────────────────────────────────────

@login_required
def loan_emi_calculate(request):
    """AJAX endpoint to calculate EMI before form submission."""
    try:
        amount  = float(request.GET.get('amount', 0))
        rate    = float(request.GET.get('rate', 0))
        months  = int(request.GET.get('months', 0))
        itype   = request.GET.get('type', 'reducing')
        import math
        if itype == 'reducing':
            r = rate / 12 / 100
            if r == 0:
                emi = amount / months
            else:
                emi = amount * r * math.pow(1 + r, months) / (math.pow(1 + r, months) - 1)
            total_payable = emi * months
        else:
            total_interest = amount * rate * months / (12 * 100)
            total_payable  = amount + total_interest
            emi = total_payable / months

        return JsonResponse({
            'emi': round(emi, 2),
            'total_payable': round(total_payable, 2),
            'total_interest': round(total_payable - amount, 2),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
