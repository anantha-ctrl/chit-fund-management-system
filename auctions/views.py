from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import Auction, Guarantor

class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['chit_group', 'month_number', 'auction_date', 'winner', 'bid_amount']
        widgets = {
            'auction_date': forms.DateInput(attrs={'type': 'date'}),
        }

class GuarantorForm(forms.ModelForm):
    class Meta:
        model = Guarantor
        fields = ['name', 'phone', 'relationship', 'id_proof_type', 'id_proof_number']

@login_required
def auction_list(request):
    auctions = Auction.objects.all().select_related('chit_group', 'winner').order_by('-auction_date')
    return render(request, 'auctions/auction_list.html', {'auctions': auctions})

@login_required
def auction_create(request):
    if request.method == 'POST':
        form = AuctionForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Auction recorded successfully.')
                return redirect('auction_list')
            except Exception as e:
                messages.error(request, 'There was an error saving the auction.')
    else:
        form = AuctionForm()
        
    return render(request, 'auctions/auction_form.html', {'form': form, 'title': 'Record Auction'})

@login_required
def auction_detail(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    form = GuarantorForm()
    return render(request, 'auctions/auction_detail.html', {'auction': auction, 'guarantor_form': form})

@login_required
def guarantor_add(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    if request.method == 'POST':
        form = GuarantorForm(request.POST)
        if form.is_valid():
            guarantor = form.save(commit=False)
            guarantor.auction = auction
            guarantor.save()
            messages.success(request, 'Guarantor added successfully.')
        else:
            messages.error(request, 'Check the form details again.')
    return redirect('auction_detail', pk=auction_id)
