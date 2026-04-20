from django.db import models
from accounts.models import User

class Member(models.Model):
    # --- Authentication & Access ---
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='member_profile')
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    
    # --- Identity (Shared) ---
    name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        blank=True
    )
    phone = models.CharField(max_length=20, unique=True)
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # --- Address (Shared) ---
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, default='Tamil Nadu')
    pincode = models.CharField(max_length=10, blank=True)
    
    # --- KYC Details (Shared) ---
    id_card_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID Type")
    id_number = models.CharField(max_length=50, blank=True, unique=True, verbose_name="Aadhar/PAN Number")
    id_proof_document = models.FileField(upload_to='members/id_proofs/', null=True, blank=True)
    photo = models.ImageField(upload_to='members/photos/', null=True, blank=True)
    
    # --- Loan Assignment (Optional) ---
    loan_agent = models.ForeignKey(
        'loan_customers.LoanAgent', 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='assigned_members'
    )

    # --- Bank Details (For payouts/disbursements) ---
    bank_name = models.CharField(max_length=150, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    
    # --- Nominee Details (Legal Backup) ---
    nominee_name = models.CharField(max_length=150, blank=True, null=True)
    nominee_relationship = models.CharField(max_length=100, blank=True, null=True)
    nominee_phone = models.CharField(max_length=20, blank=True, null=True)
    nominee_id_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nominee Aadhaar/PAN")
    
    # --- Status ---
    status = models.CharField(max_length=20, choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE')
    blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

    @property
    def full_address(self):
        parts = [self.address_line1, self.address_line2, self.city, self.state, self.pincode]
        return ', '.join(p for p in parts if p)

    @property
    def active_loan(self):
        return self.loan_set.filter(status='active').first()

    @property
    def total_loans(self):
        return self.loan_set.count()

class MemberDocument(models.Model):
    DOC_TYPES = [
        ('AADHAR', 'Aadhar Card'),
        ('PAN', 'PAN Card'),
        ('VOTER', 'Voter ID'),
        ('DRIVING', 'Driving License'),
        ('BANK', 'Bank Passbook'),
        ('OTHER', 'Other Document'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved (Verified)'),
        ('REJECTED', 'Rejected'),
    ]
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOC_TYPES)
    document_file = models.FileField(upload_to='members/documents/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True, null=True, help_text="Reason for rejection or verification notes")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.member.name} - {self.get_document_type_display()} ({self.status})"
