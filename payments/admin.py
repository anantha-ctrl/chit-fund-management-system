from django.contrib import admin
from .models import Payment, PaymentProof, CashHandover, FollowUp, PaymentQR

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('member', 'chit_group', 'installment_number', 'amount', 'status', 'due_date')
    list_filter = ('status', 'chit_group')
    search_fields = ('member__name', 'transaction_id')

@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'payment', 'transaction_id', 'status', 'submitted_at')
    list_filter = ('status',)

@admin.register(PaymentQR)
class PaymentQRAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
