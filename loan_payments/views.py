import csv
import csv
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q, Sum, F
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import date
from .models import LoanPayment, LoanTransaction, LoanPaymentProof
from .forms import LoanPaymentForm, LoanPaymentProofForm
from loans.models import Loan, EMISchedule
from payments.models import Payment
from notifications.models import Notification
from accounts.models import User


def staff_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings as s
            return redirect(s.LOGIN_URL)
        if request.user.role not in ['SUPERADMIN', 'ADMIN', 'STAFF']:
            messages.error(request, "Access denied.")
            return redirect('loan_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


def notify_admins(title, message, priority='info'):
    """Helper to send notifications to all SUPERADMIN and ADMIN users."""
    admins = User.objects.filter(role__in=['SUPERADMIN', 'ADMIN'])
    for admin in admins:
        Notification.objects.create(
            user=admin,
            title=title,
            message=message,
            priority=priority
        )


# ──────────────────────────────────────────────────────────
# RECORD PAYMENT
# ──────────────────────────────────────────────────────────

@login_required
@staff_required
def record_payment(request, loan_pk):
    """
    Record an EMI payment against a specific loan.
    Pre-fills the earliest pending/overdue EMI.
    """
    loan = get_object_or_404(Loan, pk=loan_pk, status='active')

    if request.method == 'POST':
        form = LoanPaymentForm(request.POST, loan=loan)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.loan = loan
            payment.collected_by = request.user
            payment.save()
            
            # Notify Admins
            notify_admins(
                title="Loan Payment Recorded",
                message=f"A payment of ₹{payment.amount_paid} has been recorded for {loan.customer.name} (Loan: {loan.loan_number}) by {request.user.username}.",
                priority='success'
            )
            
            messages.success(request, f"Payment of ₹{payment.amount_paid} recorded. Receipt: {payment.receipt_number}")
            return redirect('loan_payment_receipt', pk=payment.pk)
    else:
        form = LoanPaymentForm(loan=loan)

    pending_emis = loan.emi_schedule.filter(status__in=['pending', 'overdue']).count()
    return render(request, 'loan_payments/record_payment.html', {
        'loan': loan,
        'form': form,
        'pending_emis': pending_emis,
    })


# ──────────────────────────────────────────────────────────
# PAYMENT RECEIPT
# ──────────────────────────────────────────────────────────

@login_required
@staff_required
def payment_receipt(request, pk):
    """Display a printable payment receipt."""
    payment = get_object_or_404(
        LoanPayment.objects.select_related(
            'loan__customer', 'loan__branch', 'collected_by', 'emi_installment'
        ),
        pk=pk
    )
    return render(request, 'loan_payments/receipt.html', {'payment': payment})


# ──────────────────────────────────────────────────────────
# PAYMENT HISTORY
# ──────────────────────────────────────────────────────────

@login_required
@staff_required
def payment_history(request):
    """All loan EMI payments with filters."""
    qs = LoanPayment.objects.select_related(
        'loan__customer', 'collected_by', 'emi_installment'
    ).order_by('-payment_date')

    # Filters
    q = request.GET.get('q', '')
    mode = request.GET.get('mode', '')
    date_from = request.GET.get('from', '')
    date_to   = request.GET.get('to', '')

    if q:
        qs = qs.filter(
            Q(loan__loan_number__icontains=q) |
            Q(loan__customer__name__icontains=q) |
            Q(receipt_number__icontains=q)
        )
    if mode:
        qs = qs.filter(payment_mode=mode)
    if date_from:
        qs = qs.filter(payment_date__gte=date_from)
    if date_to:
        qs = qs.filter(payment_date__lte=date_to)

    # Aggregates
    total_collected = qs.aggregate(s=Sum('amount_paid'))['s'] or 0

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'loan_payments/payment_history.html', {
        'page_obj': page_obj,
        'q': q, 'mode': mode,
        'date_from': date_from, 'date_to': date_to,
        'total_collected': total_collected,
        'payment_modes': LoanPayment.PAYMENT_MODE,
    })


# ──────────────────────────────────────────────────────────
# OVERDUE EMIs
# ──────────────────────────────────────────────────────────

@login_required
@staff_required
def overdue_emis(request):
    """View all overdue EMIs across all loans."""
    today = date.today()
    qs = EMISchedule.objects.filter(
        status__in=['overdue', 'pending'],
        due_date__lt=today
    ).select_related(
        'loan__customer', 'loan__branch', 'loan__customer__loan_agent__user'
    ).order_by('due_date')

    # Filter by branch
    branch_id = request.GET.get('branch', '')
    if branch_id:
        qs = qs.filter(loan__branch_id=branch_id)

    total_overdue = qs.aggregate(
        s=Sum('emi_amount'))['s'] or 0
    total_penalty = qs.aggregate(
        s=Sum('penalty_amount'))['s'] or 0

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    from branches.models import Branch
    return render(request, 'loan_payments/overdue_emis.html', {
        'page_obj': page_obj,
        'total_overdue': total_overdue,
        'total_penalty': total_penalty,
        'branches': Branch.objects.all(),
        'branch_id': branch_id,
    })


# ──────────────────────────────────────────────────────────
# TRANSACTION LEDGER
# ──────────────────────────────────────────────────────────

@login_required
@staff_required
def transaction_ledger(request, loan_pk=None):
    """Full transaction history — optionally scoped to a single loan."""
    if loan_pk:
        loan = get_object_or_404(Loan, pk=loan_pk)
        qs = LoanTransaction.objects.filter(loan=loan).select_related('created_by')
    else:
        loan = None
        qs = LoanTransaction.objects.select_related('loan__customer', 'created_by').order_by('-created_at')

    paginator = Paginator(qs, 30)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'loan_payments/transaction_ledger.html', {
        'page_obj': page_obj,
        'loan': loan,
    })


# ──────────────────────────────────────────────────────────
# DAILY COLLECTION REPORT (quick view)
# ──────────────────────────────────────────────────────────

@login_required
@staff_required
def daily_collection(request):
    """Collection summary for today or a selected date."""
    selected_date = request.GET.get('date', str(date.today()))
    payments = LoanPayment.objects.filter(
        payment_date=selected_date
    ).select_related('loan__customer', 'collected_by', 'emi_installment')

    total = payments.aggregate(s=Sum('amount_paid'))['s'] or 0

    return render(request, 'loan_payments/daily_collection.html', {
        'payments': payments,
        'selected_date': selected_date,
        'total': total,
    })


@login_required
def customer_loan_submit_proof(request, emi_pk):
    """Allow customers to submit proof of payment for an EMI."""
    # Ensure the EMI belongs to the logged-in customer (Member)
    # The member is linked to the user via OneToOne or similar.
    # In views.py line 39, we see loan.customer. 
    # Let's check how the user is linked to Member.
    
    member = getattr(request.user, 'member_profile', None)
    if not member:
        messages.error(request, "No linked customer profile found. Please contact support.")
        return redirect('dashboard')
        
    emi = get_object_or_404(EMISchedule, pk=emi_pk, loan__customer=member)
    
    if emi.status == 'paid':
        messages.info(request, "This EMI is already marked as paid.")
        return redirect('loan_customer_portal')
    
    if hasattr(emi, 'proof'):
        if emi.proof.status == 'APPROVED':
            messages.info(request, "This EMI has been verified and approved.")
            return redirect('loan_customer_portal')
        elif emi.proof.status == 'PENDING':
            messages.info(request, "Your payment proof is currently being verified. Please wait.")
            return redirect('loan_customer_portal')
        # If REJECTED, we fall through and allow a new submission
        # We will handle deleting/updating the old proof in the POST logic

    if request.method == 'POST':
        form = LoanPaymentProofForm(request.POST, request.FILES)
        if form.is_valid():
            # If there was a rejected proof, delete it first to allow the new OneToOne mapping
            if hasattr(emi, 'proof') and emi.proof.status == 'REJECTED':
                emi.proof.delete()
                
            proof = form.save(commit=False)
            proof.emi_installment = emi
            proof.member_name = member.name
            proof.phone_no = member.phone
            proof.save()
            
            # Notify Admins
            notify_admins(
                title="New Loan Payment Proof",
                message=f"Customer {member.name} has submitted a payment proof for Loan {emi.loan.loan_number} (EMI #{emi.installment_number}). Please review it.",
                priority='warning'
            )
            
            messages.success(request, "Payment proof submitted successfully for verification.")
            return redirect('loan_customer_portal')
    else:
        # Pre-fill with member details
        initial_data = {
            'member_name': member.name,
            'phone_no': member.phone,
        }
        form = LoanPaymentProofForm(initial=initial_data)

    # ── CALCULATE TOTAL DUES (Loan + Chit) ──────────
    from django.utils import timezone
    today = timezone.now().date()
    
    # 1. Overdue Loan Dues (Across all member loans)
    loan_overdue = EMISchedule.objects.filter(
        loan__customer=member,
        status__in=['pending', 'overdue', 'partial'],
        due_date__lt=today
    ).aggregate(
        total=Sum(F('emi_amount') + F('penalty_amount') - F('paid_amount'))
    )['total'] or 0
    
    # 2. Overdue Chit Dues
    chit_overdue = Payment.objects.filter(
        member=member,
        status__in=['PENDING', 'LATE'],
        due_date__lt=today
    ).aggregate(
        total=Sum(F('amount') - F('dividend_amount') + F('penalty_amount'))
    )['total'] or 0

    total_payable = emi.emi_amount + emi.penalty_amount + loan_overdue + chit_overdue

    from payments.models import PaymentQR
    qr = PaymentQR.objects.filter(is_active=True).first()
    qr_code_url = qr.qr_code.url if qr else None

    return render(request, 'loan_payments/customer_submit_proof.html', {
        'emi': emi,
        'form': form,
        'qr_code_url': qr_code_url,
        'loan_overdue': loan_overdue,
        'chit_overdue': chit_overdue,
        'total_payable': total_payable,
    })


@login_required
@staff_required
def admin_loan_proof_list(request):
    """View for staff to see all submitted loan payment proofs."""
    status_filter = request.GET.get('status', 'PENDING')
    qs = LoanPaymentProof.objects.filter(status=status_filter).select_related(
        'emi_installment__loan__customer', 
        'emi_installment__loan__branch'
    ).order_by('-submitted_at')
    
    return render(request, 'loan_payments/admin_proof_list.html', {
        'proofs': qs,
        'status_filter': status_filter,
    })


@login_required
@staff_required
def process_loan_proof(request, proof_pk, action):
    """Approve or Reject a loan payment proof."""
    proof = get_object_or_404(LoanPaymentProof, pk=proof_pk)
    
    if proof.status != 'PENDING':
        messages.error(request, "This proof has already been processed.")
        return redirect('admin_loan_proof_list')

    if action == 'approve':
        # Create a LoanPayment record
        from .models import LoanPayment
        payment = LoanPayment.objects.create(
            loan=proof.emi_installment.loan,
            emi_installment=proof.emi_installment,
            amount_paid=proof.emi_installment.emi_amount + proof.emi_installment.penalty_amount,
            payment_mode='upi', # Assuming UPI for proofs
            transaction_reference=proof.transaction_id,
            collected_by=request.user,
            notes=f"Approved from proof submission. Member notes: {proof.member_notes or 'None'}"
        )
        proof.status = 'APPROVED'
        messages.success(request, f"Proof approved and payment recorded for {proof.emi_installment.loan.loan_number}")
    
    elif action == 'reject':
        proof.status = 'REJECTED'
        proof.admin_notes = request.POST.get('admin_notes', '')
        messages.warning(request, f"Proof rejected for {proof.emi_installment.loan.loan_number}")
    
    proof.processed_at = timezone.now()
    proof.processed_by = request.user
    proof.save()
    
    return redirect('admin_loan_proof_list')

@login_required
def export_loan_payments(request):
    if not request.user.is_superadmin():
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="loan_payments_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Loan No', 'Customer', 'Amount', 'Date', 'Mode', 'Collected By'])
    
    for lp in LoanPayment.objects.select_related('loan__customer', 'collected_by').all():
        writer.writerow([
            lp.loan.loan_number,
            lp.loan.customer.name,
            lp.amount_paid,
            lp.payment_date,
            lp.payment_mode,
            lp.collected_by.username if lp.collected_by else 'System'
        ])
    return response
