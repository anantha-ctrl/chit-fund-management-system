from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import LoanAgent
from members.models import Member
from .forms import LoanCustomerForm, LoanAgentForm
from django.conf import settings as django_settings


def staff_required(view_func):
    """Allow SUPERADMIN, ADMIN, STAFF only."""
    from functools import wraps
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(django_settings.LOGIN_URL)
        if request.user.role not in ['SUPERADMIN', 'ADMIN', 'STAFF']:
            messages.error(request, "Access denied.")
            return redirect('loan_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


# ───────────────────────────────────────────────────────────
# HELPER: auto-create/update login user for a loan customer
# ───────────────────────────────────────────────────────────

def _create_or_update_user_for_customer(customer):
    """
    Create (or update) a User login account linked to the Member (Unified Customer).
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    phone = customer.phone.strip()
    name_parts = customer.name.strip().split()
    first_name = name_parts[0] if name_parts else ''
    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

    # Already linked — just sync name/email
    if customer.user_id:
        user = customer.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = customer.email or user.email
        user.save(update_fields=['first_name', 'last_name', 'email'])
        return user, False

    # Reuse existing user with same phone username
    user = User.objects.filter(username=phone).first()
    if not user:
        user = User(
            username=phone,
            first_name=first_name,
            last_name=last_name,
            email=customer.email or '',
            role='CUSTOMER',
            is_active=True,
        )
        user.password = phone
        user.save()
        created = True
    else:
        created = False

    customer.user = user
    customer.save(update_fields=['user'])
    return user, created


# ───────────────────────────────────────────────────────────
# STAFF: LOAN CUSTOMER CRUD
# ───────────────────────────────────────────────────────────

@login_required
@staff_required
def loan_customer_list(request):
    qs = Member.objects.select_related('branch', 'loan_agent__user').order_by('-created_at')
    q = request.GET.get('q', '')
    branch_id = request.GET.get('branch', '')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(phone__icontains=q) | Q(id_number__icontains=q))
    if branch_id:
        qs = qs.filter(branch_id=branch_id)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    from branches.models import Branch
    return render(request, 'loan_customers/customer_list.html', {
        'page_obj': page_obj, 'q': q,
        'branches': Branch.objects.all(),
        'branch_id': branch_id, 'total': qs.count(),
    })


@login_required
@staff_required
def loan_customer_create(request):
    if request.method == 'POST':
        form = LoanCustomerForm(request.POST, request.FILES)
        if form.is_valid():
            phone = form.cleaned_data.get('phone')
            existing_member = Member.objects.filter(phone=phone).first()
            
            if existing_member:
                # Update existing member instead of creating a new one
                form = LoanCustomerForm(request.POST, request.FILES, instance=existing_member)
                customer = form.save()
                messages.info(request, f"Customer with phone {phone} already exists. Profile updated and linked to this loan.")
            else:
                customer = form.save(commit=False)
                customer.created_by = request.user
                customer.save()
                
            user, created = _create_or_update_user_for_customer(customer)
            if created:
                messages.success(
                    request,
                    f"Customer '{customer.name}' added. "
                    f"Login created — Username: {user.username}  |  Password: {user.username}"
                )
            else:
                messages.success(request,
                    f"Customer '{customer.name}' added. Linked to existing login: {user.username}")
            return redirect('loan_customer_detail', pk=customer.pk)
    else:
        form = LoanCustomerForm()
    return render(request, 'loan_customers/customer_form.html', {
        'form': form, 'title': 'Add Loan Customer'
    })


@login_required
@staff_required
def loan_customer_edit(request, pk):
    customer = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = LoanCustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            _create_or_update_user_for_customer(customer)
            messages.success(request, "Customer updated successfully.")
            return redirect('loan_customer_detail', pk=pk)
    else:
        form = LoanCustomerForm(instance=customer)
    return render(request, 'loan_customers/customer_form.html', {
        'form': form, 'customer': customer, 'title': 'Edit Customer'
    })


@login_required
@staff_required
def loan_customer_detail(request, pk):
    customer = get_object_or_404(
        Member.objects.select_related('branch', 'loan_agent__user', 'user'),
        pk=pk
    )
    loans = customer.loan_set.select_related('created_by').order_by('-created_at')
    return render(request, 'loan_customers/customer_detail.html', {
        'customer': customer, 'loans': loans,
    })


@login_required
@staff_required
def loan_customer_delete(request, pk):
    customer = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        name = customer.name
        customer.delete()
        messages.success(request, f"Customer '{name}' deleted.")
        return redirect('loan_customer_list')
    return render(request, 'loan_customers/customer_confirm_delete.html', {'customer': customer})


# ───────────────────────────────────────────────────────────
# AGENT VIEWS
# ───────────────────────────────────────────────────────────

@login_required
@staff_required
def loan_agent_list(request):
    agents = LoanAgent.objects.select_related('user', 'branch').annotate(
        customer_count=Count('assigned_members')
    ).order_by('user__first_name')
    return render(request, 'loan_customers/agent_list.html', {'agents': agents})


@login_required
@staff_required
def loan_agent_create(request):
    if request.user.role not in ['SUPERADMIN', 'ADMIN']:
        messages.error(request, "Only Admin can create agents.")
        return redirect('loan_agent_list')
    if request.method == 'POST':
        form = LoanAgentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Agent created successfully.")
            return redirect('loan_agent_list')
    else:
        form = LoanAgentForm()
    return render(request, 'loan_customers/agent_form.html', {'form': form})


@login_required
@staff_required
def loan_agent_edit(request, pk):
    if request.user.role not in ['SUPERADMIN', 'ADMIN']:
        messages.error(request, "Only Admin can edit agents.")
        return redirect('loan_agent_list')
    agent = get_object_or_404(LoanAgent, pk=pk)
    if request.method == 'POST':
        form = LoanAgentForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            messages.success(request, "Agent updated.")
            return redirect('loan_agent_list')
    else:
        form = LoanAgentForm(instance=agent)
    return render(request, 'loan_customers/agent_form.html', {'form': form, 'agent': agent})


@login_required
def loan_agent_api_customers(request, pk):
    """AJAX: return customers under a specific agent."""
    customers = Member.objects.filter(loan_agent_id=pk, status='ACTIVE').values('id', 'name', 'phone')
    return JsonResponse({'customers': list(customers)})


# ───────────────────────────────────────────────────────────
# AGENT PORTAL — for logged-in loan agents
# ───────────────────────────────────────────────────────────

@login_required
def loan_agent_dashboard(request):
    """Dashboard for a logged-in Loan Agent — shows their customers & collections."""
    from datetime import date, timedelta
    from loan_payments.models import LoanPayment
    from loans.models import Loan, EMISchedule
    from django.db.models import Sum, Count

    agent = getattr(request.user, 'loan_agent_profile', None)
    if not agent:
        messages.error(request, "No agent profile linked to your account.")
        return redirect('loan_dashboard')

    today = date.today()
    # All customers under this agent
    customers = agent.assigned_members.filter(status='ACTIVE').select_related('branch')
    customer_ids = customers.values_list('id', flat=True)

    # Loans for these customers
    loans_qs = Loan.objects.filter(customer_id__in=customer_ids)
    active_loans = loans_qs.filter(status='active')

    # EMI stats
    emis_qs = EMISchedule.objects.filter(loan__customer_id__in=customer_ids)
    overdue_emis = emis_qs.filter(status='overdue').select_related(
        'loan__customer'
    ).order_by('due_date')[:15]
    upcoming_emis = emis_qs.filter(
        status='pending',
        due_date__range=[today, today + timedelta(days=7)]
    ).select_related('loan__customer').order_by('due_date')[:10]

    # Today's collection by this agent
    today_collections = LoanPayment.objects.filter(
        collected_by=request.user,
        payment_date=today
    ).select_related('loan__customer', 'emi_installment')
    today_total = today_collections.aggregate(s=Sum('amount_paid'))['s'] or 0

    # Monthly collection
    month_start = today.replace(day=1)
    monthly_total = LoanPayment.objects.filter(
        collected_by=request.user,
        payment_date__gte=month_start
    ).aggregate(s=Sum('amount_paid'))['s'] or 0

    # Outstanding balance for their portfolio
    total_outstanding = active_loans.aggregate(s=Sum('outstanding_balance'))['s'] or 0

    stats = {
        'total_customers':   customers.count(),
        'active_loans':      active_loans.count(),
        'overdue_count':     emis_qs.filter(status='overdue').count(),
        'today_collection':  today_total,
        'monthly_collection': monthly_total,
        'total_outstanding': total_outstanding,
    }

    return render(request, 'loan_customers/agent_dashboard.html', {
        'agent': agent,
        'customers': customers[:10],
        'overdue_emis': overdue_emis,
        'upcoming_emis': upcoming_emis,
        'today_collections': today_collections,
        'stats': stats,
    })


# ───────────────────────────────────────────────────────────
# CUSTOMER PORTAL — for logged-in loan customers
# ───────────────────────────────────────────────────────────

def _get_loan_customer(request):
    """Return linked Member (Unified Customer) or None."""
    return getattr(request.user, 'member_profile', None)


@login_required
def loan_customer_portal(request):
    """Loan Customer self-service dashboard."""
    customer = _get_loan_customer(request)
    if not customer:
        messages.error(request, "No loan customer profile found.")
        return redirect('dashboard')

    from loans.models import Loan, EMISchedule
    from loan_payments.models import LoanPayment
    from datetime import date, timedelta

    # Include active, approved, and default loans as "ongoing"
    loans = customer.loan_set.order_by('-created_at')
    active_loan = loans.filter(status__in=['active', 'approved', 'default']).first()
    today = date.today()

    upcoming_emis = []
    overdue_emis  = []
    if active_loan:
        # For the dashboard, show EMIs that are pending and due soon
        upcoming_emis = list(active_loan.emi_schedule.filter(
            status='pending',
            due_date__range=[today, today + timedelta(days=30)]
        ).order_by('due_date')[:5])
        
        # Overdue EMIs (unpaid and past due)
        overdue_emis = list(active_loan.emi_schedule.filter(
            status__in=['overdue', 'pending'],
            due_date__lt=today
        ).order_by('due_date'))

    recent_payments = LoanPayment.objects.filter(
        loan__customer=customer
    ).select_related('emi_installment', 'loan').order_by('-payment_date')[:5]

    total_outstanding = loans.filter(status='active').aggregate(
        s=Sum('outstanding_balance'))['s'] or 0

    total_overdue = 0
    for emi in overdue_emis:
        total_overdue += emi.balance_due

    return render(request, 'loan_customers/portal/dashboard.html', {
        'customer': customer,
        'loans': loans,
        'active_loan': active_loan,
        'upcoming_emis': upcoming_emis,
        'overdue_emis': overdue_emis,
        'total_overdue_amount': total_overdue,
        'recent_payments': recent_payments,
        'total_outstanding': total_outstanding,
    })


@login_required
def loan_customer_my_loans(request):
    """All loans for the logged-in customer."""
    customer = _get_loan_customer(request)
    if not customer:
        return redirect('dashboard')
    loans = customer.loan_set.order_by('-created_at')
    return render(request, 'loan_customers/portal/my_loans.html', {
        'customer': customer, 'loans': loans
    })


@login_required
def loan_customer_my_emi(request, loan_pk):
    """EMI schedule for a specific loan (customer can only view their own)."""
    customer = _get_loan_customer(request)
    if not customer:
        return redirect('dashboard')
    from loans.models import Loan
    loan = get_object_or_404(Loan, pk=loan_pk, customer=customer)
    
    # Proactive generation if missing
    if not loan.emi_schedule.exists() and loan.status not in ['rejected', 'closed']:
        from loans.utils import generate_emi_schedule
        generate_emi_schedule(loan)
        
    schedule = loan.emi_schedule.all()
    emi_stats = {
        'paid': 0,
        'overdue': 0,
        'upcoming': 0,
    }
    for emi in schedule:
        d_status = emi.dynamic_status
        if d_status == 'PAID':
            emi_stats['paid'] += 1
        elif d_status == 'OVERDUE':
            emi_stats['overdue'] += 1
        else:
            # OPEN or UPCOMING
            emi_stats['upcoming'] += 1
    return render(request, 'loan_customers/portal/my_emi.html', {
        'customer': customer, 'loan': loan, 'schedule': schedule,
        'emi_stats': emi_stats,
    })


@login_required
def loan_customer_my_payments(request):
    """Payment history for the logged-in customer."""
    customer = _get_loan_customer(request)
    if not customer:
        return redirect('dashboard')
    from loan_payments.models import LoanPayment
    payments = LoanPayment.objects.filter(
        loan__customer=customer
    ).select_related('loan', 'emi_installment').order_by('-payment_date')
    return render(request, 'loan_customers/portal/my_payments.html', {
        'customer': customer, 'payments': payments
    })
