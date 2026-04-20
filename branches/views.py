from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Branch
from django import forms
from django.utils import timezone
import datetime
from django.db.models import Sum
from chits.models import ChitGroup
from members.models import Member
from payments.models import Payment
from loan_payments.models import LoanPayment
from loans.models import Loan

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'gstin', 'address', 'phone', 'email', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Chennai Office'}),
            'gstin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '15-digit GSTIN Number'}),
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

@login_required
@user_passes_test(is_superadmin)
def branch_analytics(request):
    branches = Branch.objects.all().order_by('name')
    
    branch_data = []
    global_total_members = 0
    global_total_collections = 0
    
    now = timezone.now()
    first_of_m = now.replace(day=1, hour=0, minute=0, second=0)
    thirty_days_ago = now - datetime.timedelta(days=30)

    for branch in branches:
        # Metrics for the month (Chit)
        current_month_chit = Payment.objects.filter(
            member__branch=branch,
            status='PAID',
            payment_date__gte=first_of_m
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Metrics for the month (Loan)
        current_month_loan = LoanPayment.objects.filter(
            loan__customer__branch=branch,
            payment_date__gte=first_of_m
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

        # Overall lifetime
        total_lifetime_chit = Payment.objects.filter(
            member__branch=branch, 
            status='PAID'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_lifetime_loan = LoanPayment.objects.filter(
            loan__customer__branch=branch
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        
        member_count = Member.objects.filter(branch=branch).count()
        chit_count = ChitGroup.objects.filter(branch=branch).count()
        loan_count = Loan.objects.filter(customer__branch=branch).count()
        
        branch_data.append({
            'branch': branch,
            'member_count': member_count,
            'chit_count': chit_count,
            'loan_count': loan_count,
            'current_month_collections': float(current_month_chit) + float(current_month_loan),
            'current_month_chit': current_month_chit,
            'current_month_loan': current_month_loan,
            'collections': float(total_lifetime_chit) + float(total_lifetime_loan),
            'new_members': Member.objects.filter(branch=branch, created_at__gt=thirty_days_ago).count(),
            'activity_ratio': round((Payment.objects.filter(member__branch=branch, payment_date__gt=thirty_days_ago).values('member').distinct().count() / member_count * 100), 1) if member_count > 0 else 0
        })
        
        global_total_members += member_count
        global_total_collections += (float(total_lifetime_chit) + float(total_lifetime_loan))

    return render(request, 'branches/branch_analytics.html', {
        'branch_data': branch_data,
        'global_total_members': global_total_members,
        'global_total_collections': global_total_collections,
        'current_month': now.strftime('%B %Y'),
        'title': 'Executive Regional Performance'
    })
