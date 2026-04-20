from django import forms
from members.models import Member
from .models import LoanAgent


class LoanCustomerForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'name', 'date_of_birth', 'gender', 'phone', 'alternate_phone',
            'email', 'address_line1', 'address_line2', 'city', 'state', 'pincode',
            'branch', 'loan_agent', 'id_card_type', 'id_number',
            'id_proof_document', 'photo',
        ]
        labels = {
            'name': 'Full Name',
            'id_number': 'PAN/Aadhaar Number',
            'id_card_type': 'ID Proof Type',
            'loan_agent': 'Assigned Agent'
        }
        widgets = {
            'name':             forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'date_of_birth':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender':           forms.Select(attrs={'class': 'form-select'}),
            'phone':            forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile'}),
            'alternate_phone':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':            forms.EmailInput(attrs={'class': 'form-control'}),
            'address_line1':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Door No, Street'}),
            'address_line2':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Landmark (optional)'}),
            'city':             forms.TextInput(attrs={'class': 'form-control'}),
            'state':            forms.TextInput(attrs={'class': 'form-control'}),
            'pincode':          forms.TextInput(attrs={'class': 'form-control'}),
            'branch':           forms.Select(attrs={'class': 'form-select'}),
            'loan_agent':       forms.Select(attrs={'class': 'form-select'}),
            'id_card_type':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Aadhaar'}),
            'id_number':        forms.TextInput(attrs={'class': 'form-control'}),
            'id_proof_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'photo':            forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if id_number:
            existing = Member.objects.filter(id_number=id_number)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                member = existing.first()
                raise forms.ValidationError(
                    f"A member with this ID number already exists: {member.name} (Phone: {member.phone})."
                )
        return id_number

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            existing = Member.objects.filter(phone=phone)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                member = existing.first()
                raise forms.ValidationError(
                    f"This phone number is already registered to {member.name}."
                )
        return phone


class LoanAgentForm(forms.ModelForm):
    class Meta:
        model = LoanAgent
        fields = ['user', 'branch', 'employee_code', 'phone', 'joined_on', 'is_active']
        widgets = {
            'user':          forms.Select(attrs={'class': 'form-select'}),
            'branch':        forms.Select(attrs={'class': 'form-select'}),
            'employee_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone':         forms.TextInput(attrs={'class': 'form-control'}),
            'joined_on':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active':     forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
