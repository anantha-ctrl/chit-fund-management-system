from django import forms
from .models import LoanPayment, LoanPaymentProof
from loans.models import EMISchedule


class LoanPaymentForm(forms.ModelForm):
    """Form for recording an EMI payment."""

    class Meta:
        model = LoanPayment
        fields = [
            'emi_installment', 'amount_paid', 'payment_date',
            'payment_mode', 'transaction_reference',
            'penalty_paid', 'penalty_waived', 'notes',
        ]
        widgets = {
            'emi_installment':      forms.Select(attrs={'class': 'form-select'}),
            'amount_paid':          forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date':         forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_mode':         forms.Select(attrs={'class': 'form-select'}),
            'transaction_reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UPI / UTR / Cheque No.'}),
            'penalty_paid':         forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'penalty_waived':       forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes':                forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, loan=None, **kwargs):
        super().__init__(*args, **kwargs)
        if loan:
            # Only show unpaid / overdue EMIs for this loan
            self.fields['emi_installment'].queryset = EMISchedule.objects.filter(
                loan=loan,
                status__in=['pending', 'overdue', 'partial']
            ).order_by('due_date')
            # Pre-fill amount from next due EMI
            next_emi = self.fields['emi_installment'].queryset.first()
            if next_emi:
                self.fields['emi_installment'].initial = next_emi
                self.fields['amount_paid'].initial = next_emi.emi_amount + next_emi.penalty_amount


class LoanPaymentProofForm(forms.ModelForm):
    class Meta:
        model = LoanPaymentProof
        fields = ['member_name', 'phone_no', 'transaction_id', 'screenshot', 'member_notes']
        widgets = {
            'member_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'phone_no': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter UPI / Transaction ID'}),
            'screenshot': forms.FileInput(attrs={'class': 'form-control'}),
            'member_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes...'}),
        }
