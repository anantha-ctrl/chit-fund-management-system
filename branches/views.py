from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Branch
from django import forms

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'code', 'address', 'phone', 'email', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Chennai Office'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. BR-01'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

def is_superadmin(user):
    return user.is_superadmin()

@login_required
@user_passes_test(is_superadmin)
def branch_list(request):
    branches = Branch.objects.all().order_by('name')
    return render(request, 'branches/branch_list.html', {'branches': branches})

@login_required
@user_passes_test(is_superadmin)
def branch_create(request):
    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch created successfully.')
            return redirect('branch_list')
    else:
        form = BranchForm()
    return render(request, 'branches/branch_form.html', {'form': form, 'title': 'Add Branch'})

@login_required
@user_passes_test(is_superadmin)
def branch_edit(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch updated successfully.')
            return redirect('branch_list')
    else:
        form = BranchForm(instance=branch)
    return render(request, 'branches/branch_form.html', {'form': form, 'title': 'Edit Branch'})

from django.db.models import Sum, Count
from members.models import Member
from payments.models import Payment
from chits.models import ChitGroup

@login_required
@user_passes_test(is_superadmin)
def branch_analytics(request):
    branches = Branch.objects.all().order_by('name')
    
    branch_data = []
    for branch in branches:
        # Calculate stats for each branch
        member_count = Member.objects.filter(branch=branch).count()
        chit_count = ChitGroup.objects.filter(branch=branch).count()
        # Collections from members belonging to this branch
        total_collections = Payment.objects.filter(member__branch=branch, status='PAID').aggregate(Sum('amount'))['amount__sum'] or 0
        
        branch_data.append({
            'branch': branch,
            'member_count': member_count,
            'chit_count': chit_count,
            'collections': total_collections,
        })
        
    return render(request, 'branches/branch_analytics.html', {
        'branch_data': branch_data,
        'title': 'Branch Performance Analytics'
    })
