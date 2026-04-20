from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from django.utils import timezone
from .models import Settlement

class SettlementForm(forms.ModelForm):
    class Meta:
        model = Settlement
        fields = ['member', 'chit_group', 'total_paid', 'total_received', 'dividend', 'penalty', 'status']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-select px-3', 'placeholder': 'Select Member'}),
            'chit_group': forms.Select(attrs={'class': 'form-select px-3', 'placeholder': 'Select Group'}),
            'total_paid': forms.NumberInput(attrs={'class': 'form-control px-3', 'placeholder': 'Total Paid'}),
            'total_received': forms.NumberInput(attrs={'class': 'form-control px-3', 'placeholder': 'Total Received'}),
            'dividend': forms.NumberInput(attrs={'class': 'form-control px-3', 'placeholder': 'Dividend'}),
            'penalty': forms.NumberInput(attrs={'class': 'form-control px-3', 'placeholder': 'Penalty'}),
            'status': forms.Select(attrs={'class': 'form-select px-3', 'placeholder': 'Select Status'}),
        }

@login_required
def settlement_list(request):
    settlements = Settlement.objects.all().select_related('member', 'chit_group')
    return render(request, 'settlements/settlement_list.html', {'settlements': settlements})

@login_required
def settlement_create(request):
    if request.method == 'POST':
        form = SettlementForm(request.POST)
        if form.is_valid():
            settlement = form.save(commit=False)
            if settlement.status == 'CLOSED':
                settlement.closed_at = timezone.now()
            settlement.save()
            messages.success(request, 'Settlement created safely.')
            return redirect('settlement_list')
    else:
        form = SettlementForm()
    
    # 2. Pre-calculate data for all Chit-Member relationships
    from chits.models import ChitMember
    from payments.models import Payment
    from auctions.models import Auction
    from django.db.models import Sum
    
    cms = ChitMember.objects.select_related('member', 'chit_group').all()
    membership_data = []
    
    for cm in cms:
        # Payout Received (if won auction)
        total_received = Auction.objects.filter(chit_group=cm.chit_group, winner=cm.member).aggregate(Total=Sum('payout_amount'))['Total'] or 0
        
        # Payment Stats
        pay_stats = Payment.objects.filter(chit_group=cm.chit_group, member=cm.member, status='PAID').aggregate(
            Paid=Sum('amount'),
            Div=Sum('dividend_amount'),
            Pen=Sum('penalty_amount')
        )
        
        membership_data.append({
            'member_id': cm.member.id,
            'group_id': cm.chit_group.id,
            'total_paid': float(pay_stats['Paid'] or 0),
            'total_received': float(total_received),
            'dividend': float(pay_stats['Div'] or 0),
            'penalty': float(pay_stats['Pen'] or 0)
        })
        
    import json
    return render(request, 'settlements/settlement_form.html', {
        'form': form, 
        'title': 'Create Settlement',
        'membership_data_json': json.dumps(membership_data)
    })

@login_required
def settlement_edit(request, pk):
    settlement = get_object_or_404(Settlement, pk=pk)
    
    # Prevent editing if closed
    if settlement.status == 'CLOSED':
        messages.error(request, 'This settlement is closed and cannot be edited.')
        return redirect('settlement_list')

    if request.method == 'POST':
        form = SettlementForm(request.POST, instance=settlement)
        if form.is_valid():
            updated_settlement = form.save(commit=False)
            if updated_settlement.status == 'CLOSED':
                updated_settlement.closed_at = timezone.now()
            updated_settlement.save()
            messages.success(request, 'Settlement updated safely.')
            return redirect('settlement_list')
    else:
        form = SettlementForm(instance=settlement)

    return render(request, 'settlements/settlement_form.html', {'form': form, 'title': 'Edit Settlement'})

@login_required
def settlement_detail(request, pk):
    settlement = get_object_or_404(Settlement, pk=pk)
    return render(request, 'settlements/settlement_detail.html', {'settlement': settlement})
