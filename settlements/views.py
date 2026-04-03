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
        
    return render(request, 'settlements/settlement_form.html', {'form': form, 'title': 'Create Settlement'})

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
