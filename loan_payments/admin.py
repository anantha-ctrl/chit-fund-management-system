from django.contrib import admin
from .models import LoanPayment, LoanTransaction


@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'loan', 'amount_paid', 'payment_mode',
                    'payment_date', 'collected_by']
    list_filter = ['payment_mode', 'payment_date']
    search_fields = ['receipt_number', 'loan__loan_number',
                     'loan__customer__full_name']
    date_hierarchy = 'payment_date'
    readonly_fields = ['receipt_number']


@admin.register(LoanTransaction)
class LoanTransactionAdmin(admin.ModelAdmin):
    list_display = ['loan', 'txn_type', 'amount', 'balance_after', 'created_at']
    list_filter = ['txn_type', 'created_at']
    search_fields = ['loan__loan_number', 'loan__customer__full_name']
    date_hierarchy = 'created_at'
