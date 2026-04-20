from django import forms
from .models import Loan
from members.models import Member


class LoanApplicationForm(forms.ModelForm):
    """Form for creating a new loan application (staff/admin use)."""

    class Meta:
        model = Loan
        fields = [
            'customer', 'branch', 'loan_type', 'loan_amount', 'interest_rate',
            'interest_type', 'tenure_months', 'start_date',
            'penalty_rate', 'grace_period_days',
            'disbursement_mode', 'notes',
        ]
        widgets = {
            'customer':         forms.Select(attrs={'class': 'form-select'}),
            'branch':           forms.Select(attrs={'class': 'form-select'}),
            'loan_type':        forms.Select(attrs={'class': 'form-select'}),
            'loan_amount':      forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '1000'}),
            'interest_rate':    forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Annual %'}),
            'interest_type':    forms.Select(attrs={'class': 'form-select'}),
            'tenure_months':    forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '360'}),
            'start_date':       forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'penalty_rate':     forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'grace_period_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '30'}),
            'disbursement_mode': forms.Select(attrs={'class': 'form-select'}),
            'notes':            forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        customer_pk = kwargs.pop('customer_pk', None)
        super().__init__(*args, **kwargs)
        
        # If we have a specific customer, lock the selection and pre-set the branch
        if customer_pk:
            customer = Member.objects.filter(pk=customer_pk).first()
            if customer:
                self.fields['customer'].queryset = Member.objects.filter(pk=customer_pk)
                self.fields['customer'].initial = customer_pk
                self.fields['branch'].initial = customer.branch
        else:
            # Show all active members for manual selection
            self.fields['customer'].queryset = Member.objects.filter(status='ACTIVE')


class LoanApprovalForm(forms.Form):
    """Simple form for approving or rejecting a loan."""
    action = forms.ChoiceField(
        choices=[('approve', 'Approve'), ('reject', 'Reject')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'rows': 3,
            'placeholder': 'Required if rejecting...'
        })
    )
    disbursement_mode = forms.ChoiceField(
        required=False,
        choices=[('', '---'), ('cash', 'Cash'), ('bank', 'Bank Transfer'), ('upi', 'UPI')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    disbursement_reference = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UTR / Transaction Ref'})
    )


class TopUpLoanForm(forms.ModelForm):
    """Form for creating a top-up loan on an existing active loan."""

    class Meta:
        model = Loan
        fields = [
            'loan_type', 'loan_amount', 'interest_rate', 'interest_type',
            'tenure_months', 'start_date',
            'penalty_rate', 'grace_period_days',
            'disbursement_mode', 'notes',
        ]
        widgets = {
            'loan_type':        forms.Select(attrs={'class': 'form-select'}),
            'loan_amount':      forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'interest_rate':    forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'interest_type':    forms.Select(attrs={'class': 'form-select'}),
            'tenure_months':    forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date':       forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'penalty_rate':     forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'grace_period_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'disbursement_mode': forms.Select(attrs={'class': 'form-select'}),
            'notes':            forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
