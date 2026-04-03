from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import Payment
from chits.models import ChitGroup

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['chit_group', 'member', 'installment_number', 'amount', 'payment_date', 'status']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

@login_required
def payment_list(request):
    payments = Payment.objects.all().select_related('chit_group', 'member').order_by('-created_at')
    return render(request, 'payments/payment_list.html', {'payments': payments})

@login_required
def payment_create(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Payment recorded successfully.')
                return redirect('payment_list')
            except Exception as e:
                messages.error(request, 'Payment for this installment already exists or is invalid.')
    else:
        form = PaymentForm()
        
    return render(request, 'payments/payment_form.html', {'form': form, 'title': 'Record Payment'})

@login_required
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment updated successfully.')
            return redirect('payment_list')
    else:
        form = PaymentForm(instance=payment)
        
    return render(request, 'payments/payment_form.html', {'form': form, 'title': 'Edit Payment'})

@login_required
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment deleted successfully.')
        return redirect('payment_list')
    return render(request, 'payments/payment_confirm_delete.html', {'payment': payment})

@login_required
def payment_receipt(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    return render(request, 'payments/payment_receipt_print.html', {'payment': payment})

@login_required
def bulk_reminder_view(request):
    from notifications.utils import send_payment_reminder
    from django.utils import timezone
    import datetime
    
    if not request.user.is_admin_or_higher():
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
        
    today = timezone.now().date()
    target_span = today + datetime.timedelta(days=3)
    pending = Payment.objects.filter(status__in=['PENDING', 'LATE'], due_date__lte=target_span)
    
    sent = 0
    for payment in pending:
        if send_payment_reminder(payment):
            sent += 1
            
    messages.success(request, f"Successfully sent digital reminders to {sent} members.")
    return redirect('payment_list')
