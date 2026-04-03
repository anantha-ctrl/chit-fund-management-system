from django.db import models
from accounts.models import User

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='member_profile')
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    
    # KYC Details
    id_number = models.CharField(max_length=50, blank=True, verbose_name="Aadhar/PAN Number")
    photo = models.ImageField(upload_to='members/photos/', null=True, blank=True)
    
    # Bank Details (For winner payouts)
    bank_name = models.CharField(max_length=150, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    
    # Nominee Details (Legal Backup)
    nominee_name = models.CharField(max_length=150, blank=True, null=True)
    nominee_relationship = models.CharField(max_length=100, blank=True, null=True)
    nominee_phone = models.CharField(max_length=20, blank=True, null=True)
    nominee_id_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nominee Aadhaar/PAN")
    
    status = models.CharField(max_length=20, choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

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
