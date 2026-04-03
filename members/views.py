from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import Member, MemberDocument
from accounts.models import User

class MemberForm(forms.ModelForm):
    username = forms.CharField(required=False, max_length=150, help_text="Optional: Create login username for customer")
    password = forms.CharField(required=False, widget=forms.PasswordInput, help_text="Optional: Set or reset password")
    
    # NEW: Link member to a Chit Group on creation
    from chits.models import ChitGroup
    chit_group = forms.ModelChoiceField(
        queryset=ChitGroup.objects.filter(status='ACTIVE'), 
        required=False, 
        label="Primary Chit Group",
        help_text="Register this member into a group immediately"
    )

    class Meta:
        model = Member
        fields = [
            'name', 'phone', 'branch', 'address', 'id_number', 'photo', 
            'bank_name', 'account_number', 'ifsc_code',
            'nominee_name', 'nominee_relationship', 'nominee_phone', 'nominee_id_number',
            'status'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        if self.instance.pk:
            # Load current groups if editing
            from chits.models import ChitMember
            initial_groups = ChitMember.objects.filter(member=self.instance)
            if initial_groups.exists():
                self.fields['chit_group'].initial = initial_groups.first().chit_group
            
            if self.instance.user:
                self.fields['username'].initial = self.instance.user.username
                self.fields['username'].widget.attrs['readonly'] = True
                self.fields['username'].help_text = "Customer already has a linked login account."
                self.fields['password'].help_text = "Type a new password to physically reset it, or leave blank to keep original."
            
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
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and not self.instance.user and not password:
            self.add_error('password', 'A password is required when creating a new login for the first time.')
        return cleaned_data

    def save(self, commit=True):
        # 1. Save the basic member data
        member = super().save(commit=commit)
        
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        # 2. Handle Linked User Creation (for Portal Access)
        if username:
            from accounts.models import User
            if not member.user:
                # Create NEW User account with explicit activation
                new_user = User.objects.create(
                    username=username, 
                    role='CUSTOMER',
                    is_active=True
                )
                new_user.set_password(password) # Custom RAW setter
                new_user.save()
                member.user = new_user
                member.save()
            elif password:
                # Update existing password with custom RAW setter
                member.user.set_password(password)
                member.user.save()
        
        # 3. Link to selected chit group
        selected_group = self.cleaned_data.get('chit_group')
        if selected_group:
            from chits.models import ChitMember
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
    payments = Payment.objects.filter(member=member).order_by('-installment_number')
    
    return render(request, 'members/member_detail.html', {
        'member': member,
        'settlements': settlements,
        'payments': payments
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
    
    # Simple logic to determine compliance status
    for member in members:
        member.doc_count = member.documents.count()
        member.has_bank_info = all([member.bank_name, member.account_number, member.ifsc_code])
        member.has_photo = bool(member.photo)
        
        # Determine status color
        if member.doc_count >= 2 and member.has_bank_info and member.has_photo:
            member.kyc_status = 'COMPLIANT'
        elif member.doc_count > 0 or member.has_bank_info:
            member.kyc_status = 'PARTIAL'
        else:
            member.kyc_status = 'PENDING'

    return render(request, 'members/kyc_center.html', {'members': members})
