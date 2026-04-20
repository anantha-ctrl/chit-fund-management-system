from django.contrib import admin
from .models import Member

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'branch', 'loan_agent', 'status', 'created_at']
    list_filter = ['status', 'branch', 'gender']
    search_fields = ['name', 'phone', 'id_number', 'email']
    fieldsets = (
        ('Personal Info', {
            'fields': ('user', 'name', 'date_of_birth', 'gender', 'photo')
        }),
        ('Contact Details', {
            'fields': ('phone', 'alternate_phone', 'email')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'pincode')
        }),
        ('KYC & Verification', {
            'fields': ('id_card_type', 'id_number', 'id_proof_document', 'blacklisted', 'blacklist_reason')
        }),
        ('Assignment', {
            'fields': ('branch', 'loan_agent')
        }),
        ('Status', {
            'fields': ('status', 'created_at')
        }),
    )
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
