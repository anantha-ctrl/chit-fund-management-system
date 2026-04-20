from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import Member, MemberDocument
from accounts.models import User

from chits.models import ChitGroup, ChitMember

class MemberForm(forms.ModelForm):
    username = forms.CharField(required=False, max_length=150, help_text="Optional: Leave blank to use member's name as login")
    password = forms.CharField(required=False, widget=forms.PasswordInput, help_text="Optional: Leave blank to use phone number as password")
    
    chit_group = forms.ModelChoiceField(
        queryset=ChitGroup.objects.filter(status='ACTIVE'), 
        required=False, 
        label="Primary Chit Group",
        help_text="Register this member into a group immediately"
    )

    class Meta:
        model = Member
        fields = [
            'name', 'phone', 'alternate_phone', 'email', 'branch',
            'address_line1', 'address_line2', 'city', 'state', 'pincode',
            'id_card_type', 'id_number', 'id_proof_document', 'photo', 
            'bank_name', 'account_number', 'ifsc_code',
            'nominee_name', 'nominee_relationship', 'nominee_phone', 'nominee_id_number',
            'status'
        ]
        widgets = {
            'address_line1': forms.TextInput(attrs={'placeholder': 'Door No / Street'}),
            'address_line2': forms.TextInput(attrs={'placeholder': 'Landmark / Area'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        if self.instance.pk:
            initial_groups = ChitMember.objects.filter(member=self.instance)
            if initial_groups.exists():
                self.fields['chit_group'].initial = initial_groups.first().chit_group
            
            if self.instance.user:
                self.fields['username'].initial = self.instance.user.username
                self.fields['username'].widget.attrs['readonly'] = True
                self.fields['username'].help_text = "Customer already has a linked login account."
                self.fields['password'].help_text = "Type a new password to physically reset it, or leave blank to keep original."
            
    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if id_number:
            existing = Member.objects.filter(id_number=id_number)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                member = existing.first()
                raise forms.ValidationError(
                    f"A member with this ID number already exists: {member.name} (Phone: {member.phone}). "
                    "Please check if this individual is already registered."
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
                    f"This phone number is already registered to {member.name}. "
                    "Duplicate phone numbers are not allowed for primary contact."
                )
        return phone

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            query = User.objects.filter(username=username)
            if self.instance.pk and self.instance.user:
                query = query.exclude(pk=self.instance.user.pk)
            if query.exists():
                raise forms.ValidationError("This username is already taken by another user.")
        return username

    def clean(self):
        return super().clean()

    def save(self, commit=True):
        member = super().save(commit=commit)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        # Auto-generate credentials for new members if not provided
        if not member.user:
            from django.utils.text import slugify
            
            if not username:
                # Create clean username from name
                base_username = slugify(member.name).replace('-', '') or 'member'
                username = base_username
                # Handle potential duplicate usernames
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
            
            if not password:
                # Default password is their phone number
                password = member.phone

        if username:
            from accounts.models import User
            if not member.user:
                new_user = User.objects.create(username=username, role='CUSTOMER', is_active=True)
                new_user.set_password(password)
                new_user.save()
                member.user = new_user
                member.save()
            elif password:
                member.user.set_password(password)
                member.user.save()
        
        selected_group = self.cleaned_data.get('chit_group')
        if selected_group:
            if not ChitMember.objects.filter(member=member, chit_group=selected_group).exists():
                ChitMember.objects.create(member=member, chit_group=selected_group)
                
        return member

class MemberDocumentForm(forms.ModelForm):
    class Meta:
        model = MemberDocument
        fields = ['document_type', 'document_file']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control rounded-pill px-3 mt-2'})

@login_required
def member_list(request):
    query = request.GET.get('q', '')
    if query:
        members = Member.objects.filter(name__icontains=query) | Member.objects.filter(phone__icontains=query)
    else:
        members = Member.objects.all()
    return render(request, 'members/member_list.html', {'members': members, 'query': query})

@login_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    # Get settlement info if it exists
    from settlements.models import Settlement
    settlements = Settlement.objects.filter(member=member)
    
    # Get payments
    from payments.models import Payment
    from chits.models import ChitMember
    payments = Payment.objects.filter(member=member).order_by('-installment_number')
    
    # Strict KYC Verification Logic
    # 1. Must have at least 2 documents (as per compliance rules)
    # 2. ALL uploaded documents MUST be APPROVED. If any are REJECTED or PENDING, kyc_verified = False.
    total_docs = member.documents.count()
    approved_docs = member.documents.filter(status='APPROVED').count()
    
    kyc_verified = (total_docs >= 2) and (total_docs == approved_docs)
    
    # Portfolio Memberships (for Passbook Access)
    chit_memberships = ChitMember.objects.filter(member=member).select_related('chit_group')
    
    return render(request, 'members/member_detail.html', {
        'member': member,
        'kyc_verified': kyc_verified,
        'settlements': settlements,
        'payments': payments,
        'chit_memberships': chit_memberships,
    })

@login_required
def member_create(request):
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member created successfully.')
            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'members/member_form.html', {'form': form, 'title': 'Create Member'})

@login_required
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member updated successfully.')
            return redirect('member_list')
    else:
        form = MemberForm(instance=member)
    return render(request, 'members/member_form.html', {'form': form, 'title': 'Edit Member'})

@login_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.delete()
        messages.success(request, 'Member deleted successfully.')
        return redirect('member_list')
    return render(request, 'members/member_confirm_delete.html', {'member': member})

@login_required
def member_document_upload(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.member = member
            document.save()
            messages.success(request, f'Successfully uploaded {document.get_document_type_display()} for {member.name}.')
            return redirect('member_detail', pk=member.pk)
    else:
        form = MemberDocumentForm()
    
    return render(request, 'members/document_upload_form.html', {
        'form': form,
        'member': member
    })

@login_required
def kyc_center(request):
    """Centralized view for monitoring member compliance and documents"""
    members = Member.objects.prefetch_related('documents').all().order_by('name')
    
    # Logic to determine compliance status
    for member in members:
        # Only count documents that have been APPROVED by admin
        member.approved_doc_count = member.documents.filter(status='APPROVED').count()
        member.total_doc_count = member.documents.count()
        
        member.has_bank_info = all([member.bank_name, member.account_number, member.ifsc_code])
        member.has_photo = bool(member.photo)
        
        # Detailed Status Logic
        all_docs_approved = (member.total_doc_count > 0 and member.approved_doc_count == member.total_doc_count)
        any_doc_rejected = member.documents.filter(status='REJECTED').exists()
        
        if member.approved_doc_count >= 2 and all_docs_approved and member.has_bank_info and member.has_photo:
            member.kyc_status = 'COMPLIANT'
        elif any_doc_rejected:
            member.kyc_status = 'REJECTED'
        elif all_docs_approved:
            member.kyc_status = 'VERIFIED'
        elif member.approved_doc_count > 0 or member.has_bank_info or member.has_photo:
            member.kyc_status = 'PARTIAL'
        else:
            member.kyc_status = 'PENDING'

    compliant_count = sum(1 for m in members if m.kyc_status == 'COMPLIANT')
    pending_count = sum(1 for m in members if any(doc.status == 'PENDING' for doc in m.documents.all()))
    missing_count = sum(1 for m in members if m.kyc_status in ['PARTIAL', 'PENDING'])

    context = {
        'members': members,
        'compliant_count': compliant_count,
        'pending_count': pending_count,
        'missing_count': missing_count,
    }
    return render(request, 'members/kyc_center.html', context)
