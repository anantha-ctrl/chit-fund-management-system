from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import TruncMonth
from datetime import date
from loans.models import Loan, EMISchedule
from loan_payments.models import LoanPayment
# LoanCustomer removed in favor of Member
from branches.models import Branch


def staff_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings as s
            return redirect(s.LOGIN_URL)
        if request.user.role not in ['SUPERADMIN', 'ADMIN', 'STAFF']:
            from django.contrib import messages
            messages.error(request, "Access denied.")
            from django.shortcuts import redirect
            return redirect('loan_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


@login_required
@staff_required
def loan_summary_report(request):
    """
    Overall loan portfolio summary with branch-wise breakdown.
    """
    branch_id = request.GET.get('branch', '')
    status_filter = request.GET.get('status', '')

    loans_qs = Loan.objects.all()
    if branch_id:
        loans_qs = loans_qs.filter(branch_id=branch_id)
    if status_filter:
        loans_qs = loans_qs.filter(status=status_filter)

    # ── Aggregated stats ──────────────────────────
    stats = {
        'total_loans':   loans_qs.count(),
        'total_amount':  loans_qs.aggregate(s=Sum('loan_amount'))['s'] or 0,
        'total_outstanding': loans_qs.filter(status='active').aggregate(
                              s=Sum('outstanding_balance'))['s'] or 0,
        'total_collected': LoanPayment.objects.filter(
                              loan__in=loans_qs).aggregate(s=Sum('amount_paid'))['s'] or 0,
        'by_status': loans_qs.values('status').annotate(
                              count=Count('id'), total=Sum('loan_amount')).order_by('status'),
    }

    # ── Branch-wise performance ───────────────────
    branch_wise = Loan.objects.values(
        'branch__name'
    ).annotate(
        loan_count=Count('id'),
        disbursed=Sum('loan_amount'),
        outstanding=Sum('outstanding_balance'),
        active=Count('id', filter=Q(status='active')),
        closed=Count('id', filter=Q(status='closed')),
        default=Count('id', filter=Q(status='default')),
    ).order_by('-disbursed')

    return render(request, 'loan_reports/loan_summary.html', {
        'stats': stats,
        'branch_wise': branch_wise,
        'branches': Branch.objects.all(),
        'branch_id': branch_id,
        'status_filter': status_filter,
        'status_choices': Loan.STATUS_CHOICES,
    })


@login_required
@staff_required
def pending_emi_report(request):
    """
    Report of all pending (upcoming) EMIs with customer & branch info.
    Filterable by branch and upcoming date range.
    """
    today = date.today()
    days = int(request.GET.get('days', 30))
    branch_id = request.GET.get('branch', '')

    from datetime import timedelta
    future_date = today + timedelta(days=days)

    qs = EMISchedule.objects.filter(
        status='pending',
        due_date__lte=future_date
    ).select_related('loan__customer', 'loan__branch', 'loan__customer__loan_agent__user')

    if branch_id:
        qs = qs.filter(loan__branch_id=branch_id)

    total_pending = qs.aggregate(s=Sum('emi_amount'))['s'] or 0

    return render(request, 'loan_reports/pending_emi.html', {
        'emis': qs.order_by('due_date'),
        'total_pending': total_pending,
        'days': days,
        'branches': Branch.objects.all(),
        'branch_id': branch_id,
    })


@login_required
@staff_required
def overdue_report(request):
    """
    Lists all customers with overdue EMIs.
    """
    today = date.today()
    branch_id = request.GET.get('branch', '')

    qs = EMISchedule.objects.filter(
        status='overdue'
    ).select_related('loan__customer', 'loan__branch', 'loan__customer__loan_agent__user')

    if branch_id:
        qs = qs.filter(loan__branch_id=branch_id)

    total_overdue_amount = qs.aggregate(s=Sum('emi_amount'))['s'] or 0
    total_penalty = qs.aggregate(s=Sum('penalty_amount'))['s'] or 0

    return render(request, 'loan_reports/overdue_report.html', {
        'emis': qs.order_by('due_date'),
        'total_overdue_amount': total_overdue_amount,
        'total_penalty': total_penalty,
        'branches': Branch.objects.all(),
        'branch_id': branch_id,
    })


@login_required
@staff_required
def branch_performance_report(request):
    """
    Branch-wise performance: loans disbursed, collections, default rate.
    """
    data = Branch.objects.annotate(
        total_loans=Count('loans'),
        total_disbursed=Sum('loans__loan_amount'),
        total_outstanding=Sum('loans__outstanding_balance'),
        active_loans=Count('loans', filter=Q(loans__status='active')),
        closed_loans=Count('loans', filter=Q(loans__status='closed')),
        default_loans=Count('loans', filter=Q(loans__status='default')),
        total_customers=Count('members'),
    ).order_by('-total_disbursed')

    return render(request, 'loan_reports/branch_performance.html', {'branches': data})


@login_required
@staff_required
def monthly_collection_report(request):
    """
    Monthly collection trend for the last 12 months.
    """
    monthly = LoanPayment.objects.annotate(
        month=TruncMonth('payment_date')
    ).values('month').annotate(
        total=Sum('amount_paid'),
        count=Count('id'),
        avg=Avg('amount_paid')
    ).order_by('-month')[:12]

    return render(request, 'loan_reports/monthly_collection.html', {
        'monthly': monthly,
    })
