from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from members.models import Member
from payments.models import Payment
from django.db.models import Sum

@login_required
def member_ledger(request, member_id):
    """Generates a full statement/ledger for a specific member"""
    member = get_object_or_404(Member, pk=member_id)
    payments = Payment.objects.filter(member=member).order_by('payment_date', 'installment_number')
    
    total_paid = payments.filter(status='PAID').aggregate(Sum('amount'))['amount__sum'] or 0
    total_dividend = payments.aggregate(Sum('dividend_amount'))['dividend_amount__sum'] or 0
    total_penalty = payments.aggregate(Sum('penalty_amount'))['penalty_amount__sum'] or 0

    context = {
        'member': member,
        'payments': payments,
        'total_paid': total_paid,
        'total_dividend': total_dividend,
        'total_penalty': total_penalty,
        'net_investment': total_paid - total_dividend + total_penalty
    }
    return render(request, 'reports_export/member_ledger.html', context)
